import datetime
import os
import urllib.request
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, SubElement
from typing import Optional

# Use defusedxml for parsing untrusted XML
import defusedxml.ElementTree as ET
from defusedxml.minidom import parseString

from api.db import topic_db
from api.models import Article
from news.converter.converter_interface import Converter
from utils.logging import debug, error, info, warning


def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")


def is_file_path(path: str) -> bool:
    parsed = urlparse(path)
    return parsed.scheme == "" or parsed.scheme == "file"


class PodcastEpisodeRSSConverter(Converter):
    """Converter for generating and updating podcast RSS feeds with episodes."""

    @staticmethod
    def can_handle(type_str: str) -> bool:
        return type_str.startswith("podcast-episode-rss")

    @staticmethod
    def convert_representation(type_str: str, article: Article) -> bool:
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

        url_parts = parts[1].split(",", 1)
        debug("PODCAST", "URL parts", str(url_parts))
        rss_url = url_parts[0]
        mp3_url = url_parts[1] if len(url_parts) > 1 else None

        info("PODCAST", "Processing", f"RSS URL: {rss_url}, MP3 URL: {mp3_url}")

        topic = topic_db.get_topic(article.topic_id)
        if not topic:
            error("PODCAST", "Topic not found", f"Cannot find topic for article {article.id}")
            return False

        existing_rss = None
        try:
            if is_safe_url(rss_url):
                req = urllib.request.Request(url=rss_url, headers={"User-Agent": "podcast-rss-converter"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    existing_rss = response.read().decode("utf-8")
            elif is_file_path(rss_url) and os.path.exists(rss_url):
                with open(rss_url, "r", encoding="utf-8") as f:
                    existing_rss = f.read()
            else:
                error("PODCAST", "Invalid URL", f"Unsafe URL scheme or file not found: {rss_url}")
                return False
        except Exception as e:
            warning("PODCAST", "RSS fetch failed", str(e))

        file_size = PodcastEpisodeRSSConverter._get_mp3_file_size(article)

        rss_xml = PodcastEpisodeRSSConverter._generate_or_update_rss(
            article, topic, mp3_url, file_size, existing_rss
        )

        article.add_representation(type_str, rss_xml, {"extension": "xml"})

        info("PODCAST", "RSS updated", f"Article: {article.title}, ID: {article.id}")
        return True

    @staticmethod
    def _get_mp3_file_size(article: Article) -> int:
        for rep in article.representations:
            if getattr(rep.metadata, "format", "") == "mp3":
                rep_data = rep.content
                if isinstance(rep_data, bytes):
                    return len(rep_data)
                elif isinstance(rep_data, str):
                    try:
                        binary_data = bytes.fromhex(rep_data)
                        return len(binary_data)
                    except ValueError:
                        return len(rep_data.encode("utf-8"))
        return 0

    @staticmethod
    def _generate_or_update_rss(
        article: Article,
        topic,
        mp3_url: Optional[str],
        file_size: int,
        existing_rss: Optional[str] = None,
    ) -> str:
        episode_item = PodcastEpisodeRSSConverter._generate_episode_element(
            article, topic, mp3_url, file_size
        )

        if existing_rss:
            try:
                rss = ET.fromstring(existing_rss)
                channel = rss.find("channel")
                if channel is None:
                    error("PODCAST", "Invalid RSS", "No channel element found")
                    return PodcastEpisodeRSSConverter._create_new_rss(article, topic, episode_item)

                guid_value = article.id
                existing_items = channel.findall("item")

                for item in existing_items:
                    guid = item.find("guid")
                    if guid is not None and guid.text == guid_value:
                        channel.remove(item)
                        break

                channel.append(episode_item)

                last_build_date = channel.find("lastBuildDate")
                if last_build_date is not None:
                    last_build_date.text = datetime.datetime.now().strftime(
                        "%a, %d %b %Y %H:%M:%S GMT"
                    )

                xml_string = ET.tostring(rss, "utf-8")
                pretty_xml = parseString(xml_string).toprettyxml(indent="  ")
                return pretty_xml

            except Exception as e:
                error("PODCAST", "RSS update failed", str(e))
                return PodcastEpisodeRSSConverter._create_new_rss(article, topic, episode_item)
        else:
            return PodcastEpisodeRSSConverter._create_new_rss(article, topic, episode_item)

    @staticmethod
    def _create_new_rss(article: Article, topic, episode_item) -> str:
        rss = Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

        channel = SubElement(rss, "channel")
        SubElement(channel, "title").text = topic.name
        SubElement(channel, "link").text = "https://example.com/podcast"
        SubElement(channel, "language").text = "en-us"
        SubElement(channel, "itunes:explicit").text = "false"
        SubElement(channel, "description").text = topic.description
        SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        channel.append(episode_item)

        xml_string = ET.tostring(rss, "utf-8")
        pretty_xml = parseString(xml_string).toprettyxml(indent="  ")
        return pretty_xml

    @staticmethod
    def _generate_episode_element(
        article: Article, topic, mp3_url: Optional[str], file_size: int
    ):
        item = Element("item")

        SubElement(item, "title").text = article.title
        SubElement(item, "guid").text = article.id
        SubElement(item, "guid").set("isPermaLink", "false")

        pub_date = SubElement(item, "pubDate")
        pub_date.text = article.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")

        if article.representations:
            content = article.representations[-1].content
            debug("PODCAST", "Using previous representation", f"Type: {article.representations[-1].type}")
        else:
            content = article.content
            debug("PODCAST", "No previous representations", "Using original article content")

        description = SubElement(item, "description")
        description.text = content[:200] + "..." if len(content) > 200 else content

        content_encoded = SubElement(item, "content:encoded")
        content_encoded.text = f"<![CDATA[{content}]]>"

        if mp3_url:
            enclosure = SubElement(item, "enclosure")
            enclosure.set("url", mp3_url)
            enclosure.set("type", "audio/mpeg")
            enclosure.set("length", str(file_size))

        return item

