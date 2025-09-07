import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
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
)

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b:together",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import asyncio

class WebIntel:
    def __init__(self):
        self.ua = UserAgent()
        self.setup_browser()
    
    def setup_browser(self):
        """Undetectable browser for agent scraping"""
        options = Options()
        options.add_argument(f'--user-agent={self.ua.random}')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = uc.Chrome(options=options)
    
    async def real_time_web_scan(self, urls, search_terms):
        """Continuous web monitoring for agents"""
        results = {}
        for url in urls:
            try:
                self.driver.get(url)
                page_source = self.driver.page_source
                
                # Search for relevant intelligence
                intel = self.extract_intelligence(page_source, search_terms)
                results[url] = intel
                
            except Exception as e:
                results[url] = f"Error: {e}"
                
        return results
    
    def extract_intelligence(self, html, terms):
        """Extract relevant info for agent decision-making"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        intelligence = {
            'headlines': [h.text for h in soup.find_all(['h1', 'h2', 'h3'])[:5]],
            'relevant_text': [],
            'links': [a['href'] for a in soup.find_all('a', href=True)[:10]],
            'timestamp': datetime.now().isoformat()
        }
        
        # Search for terms relevant to agent missions
        text = soup.get_text().lower()
        for term in terms:
            if term.lower() in text:
                # Extract context around the term
                context = self.get_context(text, term, 100)
                intelligence['relevant_text'].append({
                    'term': term,
                    'context': context
                })
        
        return intelligence
