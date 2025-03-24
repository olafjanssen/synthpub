"""Converter for generating and updating podcast RSS feeds."""

import datetime
import os
import urllib.request
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, SubElement

# Use defusedxml for parsing untrusted XML
import defusedxml.ElementTree as ET
from defusedxml.minidom import parseString

from api.db import topic_db
from api.models import Article
from news.converter.converter_interface import Converter
from utils.logging import debug, error, info, warning


def is_safe_url(url: str) -> bool:
    """
    Check if a URL uses a safe scheme (http or https).

    Args:
        url: The URL to check

    Returns:
        bool: True if the URL uses a safe scheme
    """
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")


def is_file_path(path: str) -> bool:
    """
    Check if a string is a file path rather than a URL.

    Args:
        path: The path to check

    Returns:
        bool: True if the string is a file path
    """
    parsed = urlparse(path)
    return parsed.scheme == "" or parsed.scheme == "file"


class PodcastEpisodeRSSConverter(Converter):
    """Converter for generating and updating podcast RSS feeds with episodes."""

    @staticmethod
    def can_handle(type_str: str) -> bool:
        """Check if this converter can handle the given type."""
        return type_str.startswith("podcast-episode-rss")

    @staticmethod
    def convert_representation(type_str: str, article: Article) -> bool:
        """
        Convert an article into a podcast episode and add it to an RSS feed.

        Args:
            type_str: Format "podcast-episode-rss/path/to/rss.xml,http://mp3_url.mp3"
            article: The article to convert into a podcast episode

        Returns:
            bool: True if conversion succeeded
        """
        # Parse the type string to get the RSS URL and MP3 URL
        debug("PODCAST", "Parsing type string", type_str)
        parts = type_str.split("/", 1)
        debug("PODCAST", "Type parts", str(parts))
        if len(parts) < 2:
            error(
                "PODCAST",
                "Invalid format",
                f"Expected 'podcast-episode-rss/path/to/rss.xml,mp3_url', got '{type_str}'",
            )
            return False

        # Parse the URL parts - separate RSS and MP3 URLs by comma
        url_parts = parts[1].split(",", 1)
        debug("PODCAST", "URL parts", str(url_parts))
        rss_url = url_parts[0]
        mp3_url = url_parts[1] if len(url_parts) > 1 else None

        info("PODCAST", "Processing", f"RSS URL: {rss_url}, MP3 URL: {mp3_url}")

        # Get the topic for additional metadata
        topic = topic_db.get_topic(article.topic_id)
        if not topic:
            error(
                "PODCAST",
                "Topic not found",
                f"Cannot find topic for article {article.id}"
            )
            return False

        # Check if RSS file exists
        existing_rss = None
        try:
            # Try to fetch existing RSS
            if is_safe_url(rss_url):
                req = urllib.request.Request(
                    url=rss_url, headers={"User-Agent": "podcast-rss-converter"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    existing_rss = response.read().decode("utf-8")
            elif is_file_path(rss_url) and os.path.exists(rss_url):
                with open(rss_url, "r", encoding="utf-8") as f:
                    existing_rss = f.read()
            else:
                error(
                    "PODCAST",
                    "Invalid URL",
                    f"Unsafe URL scheme or file not found: {rss_url}",
                )
                return False
        except Exception as e:
            warning("PODCAST", "RSS fetch failed", str(e))
            # Continue with creating a new RSS

        # Calculate MP3 file size from representations
        file_size = PodcastEpisodeRSSConverter._get_mp3_file_size(article)

        # Generate the updated RSS XML
        rss_xml = PodcastEpisodeRSSConverter._generate_or_update_rss(
            article, topic, mp3_url, file_size, existing_rss
        )

        # Store the RSS XML in the article's representation
        article.add_representation(type_str, rss_xml, {"extension": "xml"})

        info("PODCAST", "RSS updated", f"Article: {article.title}, ID: {article.id}")
        return True

    @staticmethod
    def _get_mp3_file_size(article: Article) -> int:
        """
        Calculate the MP3 file size from representations.

        Args:
            article: The article with representations

        Returns:
            int: The file size in bytes
        """
        # Look for MP3 data in representations
        for rep in article.representations:
            # Check if it's MP3 data (binary data or has binary metadata)
            if getattr(rep.metadata, "format", "") == "mp3":
                rep_data = rep.content
                # If it's binary data
                if isinstance(rep_data, bytes):
                    return len(rep_data)
                # If it's a hex string
                elif isinstance(rep_data, str):
                    try:
                        # Try to convert hex to bytes to get size
                        binary_data = bytes.fromhex(rep_data)
                        return len(binary_data)
                    except ValueError:
                        # If not hex, might be base64 or just the content
                        return len(rep_data.encode("utf-8"))

        # Default size if no MP3 data found
        return 0

    @staticmethod
    def _generate_or_update_rss(
        article: Article,
        topic,
        mp3_url: str | None,
        file_size: int,
        existing_rss: str | None = None,
    ) -> str:
        """
        Generate a new RSS feed or update an existing one with the article as an episode.

        Args:
            article: The article to convert to an episode
            topic: The topic this article belongs to (for metadata)
            mp3_url: URL to the MP3 file
            file_size: Size of the MP3 file in bytes
            existing_rss: Existing RSS XML content (if any)

        Returns:
            String containing the updated XML RSS feed
        """
        # Generate the episode item
        episode_item = PodcastEpisodeRSSConverter._generate_episode_element(
            article, topic, mp3_url, file_size
        )

        if existing_rss:
            # Update existing RSS
            try:
                # Parse the existing RSS - using defusedxml for security
                rss = ET.fromstring(
                    existing_rss
                )  # nosec: using defusedxml.ElementTree, not vulnerable xml.etree

                # Find the channel element
                channel = rss.find("channel")
                if channel is None:
                    error("PODCAST", "Invalid RSS", "No channel element found")
                    # Create a new RSS instead
                    return PodcastEpisodeRSSConverter._create_new_rss(
                        article, topic, episode_item
                    )

                # Find if this episode already exists (by guid)
                guid_value = article.id
                existing_items = channel.findall("item")

                for item in existing_items:
                    guid = item.find("guid")
                    if guid is not None and guid.text == guid_value:
                        # Episode exists, remove it to replace with updated version
                        channel.remove(item)
                        break

                # Add the new/updated episode item
                channel.append(episode_item)

                # Update lastBuildDate
                last_build_date = channel.find("lastBuildDate")
                if last_build_date is not None:
                    last_build_date.text = datetime.datetime.now().strftime(
                        "%a, %d %b %Y %H:%M:%S GMT"
                    )

                # Convert to string with pretty formatting
                xml_string = ET.tostring(rss, "utf-8")
                pretty_xml = parseString(xml_string).toprettyxml(indent="  ")

                return pretty_xml

            except Exception as e:
                error("PODCAST", "RSS update failed", str(e))
                # Fall back to creating a new RSS
                return PodcastEpisodeRSSConverter._create_new_rss(article, topic, episode_item)
        else:
            # Create a new RSS feed
            return PodcastEpisodeRSSConverter._create_new_rss(article, topic, episode_item)

    @staticmethod
    def _create_new_rss(article: Article, topic, episode_item) -> str:
        """Create a new podcast RSS feed with the topic's project info and the episode."""
        # Create the root element
        rss = Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

        # Create the channel element
        channel = SubElement(rss, "channel")

        # Add required channel elements
        SubElement(channel, "title").text = topic.name
        SubElement(channel, "link").text = "https://example.com/podcast"
        SubElement(channel, "language").text = "en-us"
        SubElement(channel, "itunes:explicit").text = "false"
        SubElement(channel, "description").text = topic.description
        SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Add the episode to the channel
        channel.append(episode_item)

        # Convert to string with pretty formatting
        xml_string = ET.tostring(rss, "utf-8")
        pretty_xml = parseString(xml_string).toprettyxml(indent="  ")

        return pretty_xml

    @staticmethod
    def _generate_episode_element(article: Article, topic, mp3_url: str | None, file_size: int):
        """
        Generate an RSS item element for a podcast episode.

        Args:
            article: The article to convert to an episode
            topic: The topic this article belongs to (for metadata)
            mp3_url: URL to the MP3 file
            file_size: Size of the MP3 file in bytes

        Returns:
            Element representing the podcast episode
        """
        # Create the item element
        item = Element("item")

        # Add required item elements
        SubElement(item, "title").text = article.title
        SubElement(item, "guid").text = article.id
        SubElement(item, "guid").set("isPermaLink", "false")
        
        # Add publication date
        pub_date = SubElement(item, "pubDate")
        pub_date.text = article.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Get content from the latest representation or fall back to article.content
        if article.representations:
            content = article.representations[-1].content
            debug("PODCAST", "Using previous representation", f"Type: {article.representations[-1].type}")
        else:
            content = article.content
            debug("PODCAST", "No previous representations", "Using original article content")

        # Add description
        description = SubElement(item, "description")
        description.text = content[:200] + "..." if len(content) > 200 else content

        # Add content:encoded for full content
        content_encoded = SubElement(item, "content:encoded")
        content_encoded.text = f"<![CDATA[{content}]]>"

        # Add enclosure for the MP3 file if URL is provided
        if mp3_url:
            enclosure = SubElement(item, "enclosure")
            enclosure.set("url", mp3_url)
            enclosure.set("type", "audio/mpeg")
            enclosure.set("length", str(file_size))

        return item
