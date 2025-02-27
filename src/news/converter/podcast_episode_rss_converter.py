"""Converter for generating podcast episode XML for topics."""
import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from api.models import Topic
from news.converter.converter_interface import Converter

class PodcastEpisodeRSSConverter(Converter):
    """Converter for generating podcast episode XML for topics with MP3 files."""
    
    @staticmethod
    def can_handle(type: str) -> bool:
        """Check if this converter can handle the given type."""
        return type.lower() == "podcast-episode-rss"
        
    @staticmethod
    def convert_representation(type: str, topic: Topic) -> bool:
        """
        Convert a topic into podcast episode XML and store in the topic.
        
        Args:
            type: The type to convert to (should be 'podcast')
            topic: The topic to convert into a podcast episode
            
        Returns:
            bool: True if conversion succeeded
        """
            
        # Generate the episode XML
        episode_xml = PodcastEpisodeRSSConverter._generate_episode_xml(topic)
                
        topic.add_representation(type, episode_xml)
        
        print(f"Podcast episode XML generated for topic {topic.id}")
        return True
    
    @staticmethod
    def _generate_episode_xml(topic: Topic) -> str:
        """
        Generate XML for a single podcast episode.
        
        Args:
            topic: The topic to convert to episode XML
            
        Returns:
            String containing the XML for the episode
        """
        # Create the root element (item)
        item = ET.Element("item")
        
        # Add required episode elements
        ET.SubElement(item, "title").text = topic.title
        ET.SubElement(item, "description").text = topic.description
        
        # Publication date (RSS format)
        pub_date = getattr(topic, 'publication_date', datetime.datetime.now())
        ET.SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Add the MP3 enclosure
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", topic.publish_url)
        enclosure.set("type", "audio/mpeg")
        enclosure.set("length", str(getattr(topic, 'file_size', 0)))
        
        # Add a GUID - use topic ID to ensure consistency
        guid = ET.SubElement(item, "guid")
        guid.text = topic.id
        guid.set("isPermaLink", "false")
        
        # iTunes specific elements
        ET.SubElement(item, "itunes:duration").text = getattr(topic, 'duration', '00:00:00')
        ET.SubElement(item, "itunes:explicit").text = "false"
        
        # Convert to string with pretty formatting
        xml_string = ET.tostring(item, 'utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
        
        return pretty_xml
    