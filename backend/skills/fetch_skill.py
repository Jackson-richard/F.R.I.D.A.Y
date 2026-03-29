import requests
from bs4 import BeautifulSoup
from skills.base_skill import BaseSkill

class FetchWebSkill(BaseSkill):
    name = "fetch_web_content"
    description = "Read and extract text content from a web page URL. Useful for summarizing articles or reading documentation."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The full URL of the webpage to read (e.g., https://en.wikipedia.org/wiki/Python)"
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, **kwargs) -> str:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=8)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            # remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
            # extract text
            text = soup.get_text(separator=' ', strip=True)
            # truncate text to avoid blowing up context window
            capped_text = text[:8000]
            if len(text) > 8000:
                capped_text += "... [Content truncated]"
            return capped_text
        except Exception as e:
            return f"Failed to fetch content from {url}: {e}"
