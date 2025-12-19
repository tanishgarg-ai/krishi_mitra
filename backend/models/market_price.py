import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os
# from utils.llm import Base_llm
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

Base_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="qwen/qwen3-32b",
    temperature=0.5
)


class DataGovScraper:
    """Production-ready Data.gov.in scraper with web fallback (mandibhavindia.in)."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.api_key = os.getenv("DATA_GOV_API")
        self.api_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    def get_market_price(self, crop: str, location: str = "",state:str ="") -> str:
        try:
            # ✅ Build Data.gov.in API URL
            base_url = (
                f"{self.api_url}?api-key={self.api_key}"
                f"&format=json&limit=100&offset=0"
            )
            if crop:
                base_url += f"&filters[commodity]={crop.capitalize()}"
            if location:
                base_url += f"&filters[state]={location.capitalize()}"

            # ✅ Web scraping fallback URL
            base_url2 = f"https://mandibhavindia.in/commodity/{crop.lower()}"
            base_url2 = "https://mandibhavindia.in/commodity"

            if crop:
                base_url2 += f"/{crop.lower()}"

            # If both state and district are provided
            if state and location:
                base_url2 += f"/{state.lower().replace(' ', '-').replace('_', '-')}/{location.lower().replace(' ', '-').replace('_', '-')}"
            # If only state is provided
            elif state:
                base_url2 += f"/{state.lower().replace(' ', '-').replace('_', '-')}"
            # If only location (district) is provided (rare)
            elif location:
                base_url2 += f"/{location.lower().replace(' ', '-').replace('_', '-')}"

            
            print(base_url2)
            response = self.session.get(base_url2, timeout=15)

            if response.status_code != 200:
                return f"Error fetching page: HTTP {response.status_code}"

            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            # ✅ Clean the HTML before sending to LLM
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            visible_text = soup.get_text(separator="\n", strip=True)
            short_text = visible_text # avoid token overload

            prompt = (
                f"The following text is scraped from a mandi price website for crop '{crop}' "
                f"in '{location}'. Extract and summarize the current price details clearly:\n\n{short_text}"
            )

            response = Base_llm.invoke(prompt)
            formatted_result = response.content if hasattr(response, "content") else str(response)

            return formatted_result

        except Exception as e:
            return f"❌ Error: {str(e)}"
