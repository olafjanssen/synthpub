"""
Content converter using a generic llm prompt.
"""
from .converter_interface import Converter
from api.models.topic import Topic
from langchain.prompts import PromptTemplate
from src.curator.llm_utils import get_llm


class Prompt(Converter):
    
    @staticmethod
    def can_handle(type: str) -> bool:
        print(f"Checking if {type} can handle Prompt")
        return type == 'prompt'
    
    @staticmethod
    def convert_content(type: str, topic: Topic) -> bool:
        try:            
            content = topic.representations[-1].content
            
            llm = get_llm('article_refinement')
        
            prompt = PromptTemplate.from_template("""
    You are a professional radio news writer creating an engaging news segment for an international audience in Eindhoven, Netherlands. Your task is to write a clear, concise, and lively radio news script in approximately 150 words.

### 🔹 Audience Profile:
- Educated listeners, interested in a deeper understanding of current events.
- Internationally oriented locals or expatriates living in or near Eindhoven.
- Likely to be **distracted while listening**, so use **short and easy-to-follow sentences**.

### 🔹 Tone & Style:
- **If the news is about technology, crime, or health**, use a **serious and trustworthy tone**.
- **For other news (e.g., local events, culture, lifestyle, light politics)**, use a **humorous and entertaining tone** to keep it engaging.
- The style should feel **like a natural radio broadcast**, ensuring clarity and impact.

### 🔹 Structure:
1. **Start with a catchy headline** that grabs attention.
2. **Play a short jingle** to set the tone.
3. **Mention the news source explicitly** if it's from a single outlet (e.g., "According to TU Eindhoven...").
4. **Provide essential details (Who, What, Where, When, Why?)** in an engaging, conversational way.
5. **Give background context** to help listeners understand its importance.

### 🔹 Topic:
{content}

Now, generate the full radio news script, keeping it engaging, informative, and tailored to the audience.
""")

            converted_content = llm.invoke(prompt.format(content=content)).content.strip()

            topic.add_representation("text", converted_content)

            return True
            
        except Exception as e:
            print(f"Error converting {type}: {str(e)}")
            return False 