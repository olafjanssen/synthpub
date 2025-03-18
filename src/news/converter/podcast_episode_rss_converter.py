"""Converter for generating and updating podcast RSS feeds."""

import datetime
import os
import urllib.request
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, SubElement

# Use defusedxml for parsing untrusted XML
import defusedxml.ElementTree as ET
from defusedxml.minidom import parseString

from api.models import Topic
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
    def convert_representation(type_str: str, topic: Topic) -> bool:
        """
        Convert a topic into a podcast episode and add it to an RSS feed.

        Args:
            type_str: Format "podcast-episode-rss/path/to/rss.xml,http://mp3_url.mp3"
            topic: The topic to convert into a podcast episode

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

        # Calculate MP3 file size from previous representations
        file_size = PodcastEpisodeRSSConverter._get_mp3_file_size(topic)

        # Generate the updated RSS XML
        rss_xml = PodcastEpisodeRSSConverter._generate_or_update_rss(
            topic, mp3_url, file_size, existing_rss
        )

        # Store the RSS XML in the topic's representation
        topic.add_representation(type_str, rss_xml)

        info("PODCAST", "RSS updated", f"Topic: {topic.name}, ID: {topic.id}")
        return True

    @staticmethod
    def _get_mp3_file_size(topic: Topic) -> int:
        """
        Calculate the MP3 file size from previous representations.

        Args:
            topic: The topic with representations

        Returns:
            int: The file size in bytes
        """
        # Look for MP3 data in previous representations
        for rep in topic.representations:
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
        topic: Topic,
        mp3_url: str | None,
        file_size: int,
        existing_rss: str | None = None,
    ) -> str:
        """
        Generate a new RSS feed or update an existing one with the topic as an episode.

        Args:
            topic: The topic to convert to an episode
            mp3_url: URL to the MP3 file
            file_size: Size of the MP3 file in bytes
            existing_rss: Existing RSS XML content (if any)

        Returns:
            String containing the updated XML RSS feed
        """
        # Generate the episode item
        episode_item = PodcastEpisodeRSSConverter._generate_episode_element(
            topic, mp3_url, file_size
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
                        topic, episode_item
                    )

                # Find if this episode already exists (by guid)
                guid_value = topic.id
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
                return PodcastEpisodeRSSConverter._create_new_rss(topic, episode_item)
        else:
            # Create a new RSS feed
            return PodcastEpisodeRSSConverter._create_new_rss(topic, episode_item)

    @staticmethod
    def _create_new_rss(topic: Topic, episode_item) -> str:
        """Create a new podcast RSS feed with the topic's project info and the episode."""
        # Create the root element
        rss = Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

        # Create the channel element
        channel = SubElement(rss, "channel")

        # Get podcast info from project or use defaults
        project = getattr(topic, "project", None)

        # Add required channel elements
        SubElement(channel, "title").text = (
            getattr(project, "title", "Podcast") if project else "Podcast"
        )
        SubElement(channel, "link").text = (
            getattr(project, "website", "https://example.com")
            if project
            else "https://example.com"
        )
        SubElement(channel, "description").text = (
            getattr(project, "description", "Podcast description")
            if project
            else "Podcast description"
        )
        SubElement(channel, "language").text = (
            getattr(project, "language", "en-us") if project else "en-us"
        )
        SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Add iTunes specific elements
        SubElement(channel, "itunes:author").text = (
            getattr(project, "author", "Unknown") if project else "Unknown"
        )
        SubElement(channel, "itunes:summary").text = (
            getattr(project, "description", "Podcast description")
            if project
            else "Podcast description"
        )
        SubElement(channel, "itunes:explicit").text = "false"

        # Add the episode
        channel.append(episode_item)

        # Convert to string with pretty formatting
        xml_string = ET.tostring(rss, "utf-8")
        pretty_xml = parseString(xml_string).toprettyxml(indent="  ")

        return pretty_xml

    @staticmethod
    def _generate_episode_element(topic: Topic, mp3_url: str | None, file_size: int):
        """
        Generate an XML element for a podcast episode from a topic.

        Args:
            topic: The topic to convert to episode
            mp3_url: URL to the MP3 file
            file_size: Size of the MP3 file in bytes

        Returns:
            XML Element for the podcast episode
        """
        # Create the item element
        item = Element("item")

        # Add required episode elements
        SubElement(item, "title").text = topic.name
        SubElement(item, "description").text = topic.description

        # Publication date (RSS format)
        pub_date = getattr(topic, "published_at", datetime.datetime.now())
        SubElement(item, "pubDate").text = pub_date.strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Use the provided MP3 URL or fallback to a placeholder
        if not mp3_url:
            warning("PODCAST", "No MP3 URL", f"Topic: {topic.name}, ID: {topic.id}")
            mp3_url = f"https://example.com/{topic.id}.mp3"  # Placeholder

        # Add the MP3 enclosure
        enclosure = SubElement(item, "enclosure")
        enclosure.set("url", mp3_url)
        enclosure.set("type", "audio/mpeg")
        enclosure.set("length", str(file_size))

        # Add a GUID - use topic ID to ensure consistency
        guid = SubElement(item, "guid")
        guid.text = topic.id
        guid.set("isPermaLink", "false")

        # iTunes specific elements
        SubElement(item, "itunes:duration").text = getattr(
            topic, "duration", "00:00:00"
        )
        SubElement(item, "itunes:explicit").text = "false"

        return item
