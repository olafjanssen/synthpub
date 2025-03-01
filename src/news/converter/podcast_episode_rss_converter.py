"""Converter for generating and updating podcast RSS feeds."""
import os
import datetime
import urllib.request
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from xml.dom import minidom

from api.models import Topic
from news.converter.converter_interface import Converter

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
        print(f"Type string: {type_str}")
        parts = type_str.split("/", 1)
        print(f"Parts: {parts}")
        if len(parts) < 2:
            print(f"Invalid type format. Expected 'podcast-episode-rss/path/to/rss.xml,mp3_url', got '{type_str}'")
            return False
        
        # Parse the URL parts - separate RSS and MP3 URLs by comma
        url_parts = parts[1].split(",", 1)
        print(f"URL parts: {url_parts}")
        rss_url = url_parts[0]
        mp3_url = url_parts[1] if len(url_parts) > 1 else None
        
        print(f"RSS URL: {rss_url}, MP3 URL: {mp3_url}")
        
        # Check if RSS file exists
        existing_rss = None
        try:
            # Try to fetch existing RSS
            if rss_url.startswith("http://") or rss_url.startswith("https://"):
                with urllib.request.urlopen(rss_url) as response:
                    existing_rss = response.read().decode('utf-8')
            elif rss_url.startswith("file://"):
                file_path = urlparse(rss_url).path
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_rss = f.read()
            else:
                # Check if it's a local path without scheme
                if os.path.exists(rss_url):
                    with open(rss_url, 'r', encoding='utf-8') as f:
                        existing_rss = f.read()
        except Exception as e:
            print(f"Could not fetch existing RSS: {str(e)}")
            # Continue with creating a new RSS
        
        # Calculate MP3 file size from previous representations
        file_size = PodcastEpisodeRSSConverter._get_mp3_file_size(topic)
        
        # Generate the updated RSS XML
        rss_xml = PodcastEpisodeRSSConverter._generate_or_update_rss(topic, mp3_url, file_size, existing_rss)
        
        # Store the RSS XML in the topic's representation
        topic.add_representation(type_str, rss_xml)
        
        print(f"Podcast RSS generated/updated for topic {topic.id}")
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
            if getattr(rep.metadata, 'format', '') == 'mp3':
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
                        return len(rep_data.encode('utf-8'))
    
        # Default size if no MP3 data found
        return 0
    
    @staticmethod
    def _generate_or_update_rss(topic: Topic, mp3_url: str, file_size: int, existing_rss: str = None) -> str:
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
        episode_item = PodcastEpisodeRSSConverter._generate_episode_element(topic, mp3_url, file_size)
        
        if existing_rss:
            # Update existing RSS
            try:
                # Parse the existing RSS
                rss = ET.fromstring(existing_rss)
                
                # Find the channel element
                channel = rss.find("channel")
                if channel is None:
                    print("Invalid RSS: no channel element found")
                    # Create a new RSS instead
                    return PodcastEpisodeRSSConverter._create_new_rss(topic, episode_item)
                
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
                    last_build_date.text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                
                # Convert to string with pretty formatting
                xml_string = ET.tostring(rss, 'utf-8')
                pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
                
                return pretty_xml
                
            except Exception as e:
                print(f"Error updating existing RSS: {str(e)}")
                # Fall back to creating a new RSS
                return PodcastEpisodeRSSConverter._create_new_rss(topic, episode_item)
        else:
            # Create a new RSS feed
            return PodcastEpisodeRSSConverter._create_new_rss(topic, episode_item)
    
    @staticmethod
    def _create_new_rss(topic: Topic, episode_item) -> str:
        """Create a new podcast RSS feed with the topic's project info and the episode."""
        # Create the root element
        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        
        # Create the channel element
        channel = ET.SubElement(rss, "channel")
        
        # Get podcast info from project or use defaults
        project = getattr(topic, 'project', None)
        
        # Add required channel elements
        ET.SubElement(channel, "title").text = getattr(project, 'title', "Podcast") if project else "Podcast"
        ET.SubElement(channel, "link").text = getattr(project, 'website', "https://example.com") if project else "https://example.com"
        ET.SubElement(channel, "description").text = getattr(project, 'description', "Podcast description") if project else "Podcast description"
        ET.SubElement(channel, "language").text = getattr(project, 'language', "en-us") if project else "en-us"
        ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Add iTunes specific elements
        ET.SubElement(channel, "itunes:author").text = getattr(project, 'author', "Unknown") if project else "Unknown"
        ET.SubElement(channel, "itunes:summary").text = getattr(project, 'description', "Podcast description") if project else "Podcast description"
        ET.SubElement(channel, "itunes:explicit").text = "false"
        
        # Add the episode
        channel.append(episode_item)
        
        # Convert to string with pretty formatting
        xml_string = ET.tostring(rss, 'utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
        
        return pretty_xml
    
    @staticmethod
    def _generate_episode_element(topic: Topic, mp3_url: str, file_size: int):
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
        item = ET.Element("item")
        
        # Add required episode elements
        ET.SubElement(item, "title").text = topic.name
        ET.SubElement(item, "description").text = topic.description
        
        # Publication date (RSS format)
        pub_date = getattr(topic, 'published_at', datetime.datetime.now())
        ET.SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Use the provided MP3 URL or fallback to a placeholder
        if not mp3_url:
            print(f"Warning: No MP3 URL provided for topic {topic.id}")
            mp3_url = f"https://example.com/{topic.id}.mp3"  # Placeholder
            
        # Add the MP3 enclosure
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", mp3_url)
        enclosure.set("type", "audio/mpeg")
        enclosure.set("length", str(file_size))
        
        # Add a GUID - use topic ID to ensure consistency
        guid = ET.SubElement(item, "guid")
        guid.text = topic.id
        guid.set("isPermaLink", "false")
        
        # iTunes specific elements
        ET.SubElement(item, "itunes:duration").text = getattr(topic, 'duration', '00:00:00')
        ET.SubElement(item, "itunes:explicit").text = "false"
        
        return item
    