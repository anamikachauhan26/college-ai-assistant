import os, requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0 (student project bot)"}

def scrape_html_page(url, save_as):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove nav/footer/script noise before extracting text
    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.split("\n") if len(line) > 2)  # drop empty/junk lines

    with open(f"data/{save_as}", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {save_as} ({len(text)} chars)")

def download_and_extract_pdf(pdf_url, save_as):
    response = requests.get(pdf_url, headers=HEADERS, timeout=15)
    temp_path = "temp.pdf"
    with open(temp_path, "wb") as f:
        f.write(response.content)

    reader = PdfReader(temp_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    os.remove(temp_path)

    with open(f"data/{save_as}", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {save_as} ({len(text)} chars)")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # Fill these in with your college's real URLs
    scrape_html_page("https://yourcollege.edu/academics/rules", "academic_rules.txt")
    download_and_extract_pdf("https://yourcollege.edu/notices/exam-schedule.pdf", "exam_schedule.txt")
    # Add more lines like these for each real page/PDF you want