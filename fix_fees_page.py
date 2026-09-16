import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (student project - WCE college assistant)"}

def scrape_fee_page(url, save_as):
    resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", attrs={"data-elementor-type": "wp-page"}) \
                  or soup.find("div", attrs={"data-elementor-type": "single-post"})

    text = content_div.get_text(separator="\n", strip=True) if content_div else ""
    text = "\n".join(line for line in text.split("\n") if len(line) > 2)

    if content_div:
        pdf_links = content_div.find_all("a", href=lambda h: h and h.endswith(".pdf"))
        print(f"Found {len(pdf_links)} PDF links on this page")
        for link in pdf_links:
            pdf_url = link["href"]
            try:
                pdf_resp = requests.get(pdf_url, headers=HEADERS, timeout=15, verify=False)
                reader = PdfReader(BytesIO(pdf_resp.content))
                pdf_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                if pdf_text.strip():
                    label = link.get_text(strip=True) or pdf_url.split("/")[-1]
                    text += f"\n\n--- {label} ---\n\n" + pdf_text
                    print(f"  Added: {label} ({len(pdf_text)} chars)")
                else:
                    print(f"  Empty text extracted from: {pdf_url}")
            except Exception as e:
                print(f"  Failed to fetch/parse {pdf_url}: {e}")

    with open(f"data/{save_as}", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {save_as} ({len(text)} chars)")

if __name__ == "__main__":
    scrape_fee_page(
        "https://walchandsangli.ac.in/admissions/fees-as-per-authorities-dte-fra/",
        "page_1_fees-as-per-authorities-dte-fra.txt"
    )