import os, requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (student project - WCE college assistant)"}
NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def get_urls_from_sitemap(sitemap_url):
    resp = requests.get(sitemap_url, headers=HEADERS, timeout=10, verify=False)
    root = ET.fromstring(resp.content)
    return [url.find("ns:loc", NS).text for url in root.findall("ns:url", NS)]

def scrape_notice_page(url, save_as):
    resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    content_type = resp.headers.get("Content-Type", "")

    if "pdf" in content_type or url.endswith(".pdf"):
        reader = PdfReader(BytesIO(resp.content))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
    else:
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", attrs={"data-elementor-type": "single-post"})

        if content_div:
            text = content_div.get_text(separator="\n", strip=True)
        else:
            for tag in soup(["nav", "footer", "script", "style", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)

        text = "\n".join(line for line in text.split("\n") if len(line) > 2)

        if content_div:
            pdf_link = content_div.find("a", href=lambda h: h and h.endswith(".pdf"))
            if pdf_link:
                pdf_url = pdf_link["href"]
                pdf_resp = requests.get(pdf_url, headers=HEADERS, timeout=15, verify=False)
                reader = PdfReader(BytesIO(pdf_resp.content))
                pdf_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                text += "\n\n--- Linked PDF content ---\n\n" + pdf_text

    if len(text.strip()) < 20:
        print(f"Skipped (too little content): {url}")
        return

    with open(f"data/{save_as}", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {save_as} ({len(text)} chars)")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    notice_urls = get_urls_from_sitemap("https://walchandsangli.ac.in/notice_board-sitemap.xml")

    for i, url in enumerate(notice_urls[:15]):
        slug = url.rstrip("/").split("/")[-1][:50]
        scrape_notice_page(url, f"notice_{i}_{slug}.txt")