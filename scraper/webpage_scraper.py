# scraper/krtrimaiq_scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_homepage(url):
    resp = requests.get(url)
    # print(resp)
    soup = BeautifulSoup(resp.text, "html.parser")
    content = {
        "titles": [h.get_text() for h in soup.select("h2")],
        "paragraphs": [p.get_text() for p in soup.select("p")],
        "images": [img["src"] for img in soup.select("img") if img.get("src")]
    }
    return content

# if __name__ == "__main__":
#     data = scrape_homepage()
#     print("Titles:", data["titles"])
#     print("Paragraphs:", data["paragraphs"])
#     print("Images:", data["images"])