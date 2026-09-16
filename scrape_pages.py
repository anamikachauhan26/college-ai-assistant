import os, requests, time
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (student project - WCE college assistant)"}

PAGES_TO_SCRAPE = [
    "https://walchandsangli.ac.in/admissions/",
    "https://walchandsangli.ac.in/admissions/fees-as-per-authorities-dte-fra/",
    "https://walchandsangli.ac.in/admissions/first-year-btech/",
    "https://walchandsangli.ac.in/admissions/first-year-of-btech-pio-oci-fn-ciwg-nri-students/",
    "https://walchandsangli.ac.in/admissions/direct-second-year-b-tech/",
    "https://walchandsangli.ac.in/admissions/institute-level-notifications/",
    "https://walchandsangli.ac.in/academics-programmes/examination-notices-and-schedule/",
    "https://walchandsangli.ac.in/academics-programmes/calendars-and-schedules/",
    "https://walchandsangli.ac.in/academics-programmes/academic-regulations/",
    "https://walchandsangli.ac.in/academics-programmes/credit-system-and-bank/",
    "https://walchandsangli.ac.in/department-of-computer-engineering/overview/",
    "https://walchandsangli.ac.in/department-of-computer-engineering/b-tech-curriculum/",
    "https://walchandsangli.ac.in/department-of-information-technology/overview-it/",
    "https://walchandsangli.ac.in/department-of-information-technology/b-tech-curriculum-with-minors-it/",
    "https://walchandsangli.ac.in/department-of-mechanical-engineering/overview/",
    "https://walchandsangli.ac.in/department-of-mechanical-engineering/b-tech-curriculum-with-minors-mech/",
    "https://walchandsangli.ac.in/department-of-electrical-engg/overview-electrical/",
    "https://walchandsangli.ac.in/department-of-electrical-engg/b-tech-curriculum-with-minors-electrical/",
    "https://walchandsangli.ac.in/department-of-civil-engineering/overview-ce/",
    "https://walchandsangli.ac.in/department-of-civil-engineering/b-tech-curriculum-with-minors-ce/",
    "https://walchandsangli.ac.in/department-of-electronics-engg/overview-electronics/",
    "https://walchandsangli.ac.in/department-of-electronics-engg/b-tech-electronics-engineering-curriculum-electronics/",
]

def scrape_page(url, save_as):
    resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    content_type = resp.headers.get("Content-Type", "")

    if "pdf" in content_type or url.endswith(".pdf"):
        reader = PdfReader(BytesIO(resp.content))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
    else:
        soup = BeautifulSoup(resp.text, "html.parser")
        content_div = soup.find("div", attrs={"data-elementor-type": "single-post"}) \
                      or soup.find("div", attrs={"data-elementor-type": "wp-page"})

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
                try:
                    pdf_resp = requests.get(pdf_url, headers=HEADERS, timeout=15, verify=False)
                    reader = PdfReader(BytesIO(pdf_resp.content))
                    pdf_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                    text += "\n\n--- Linked PDF content ---\n\n" + pdf_text
                except Exception:
                    pass

    if len(text.strip()) < 20:
        print(f"Skipped (too little content): {url}")
        return

    with open(f"data/{save_as}", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved {save_as} ({len(text)} chars)")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for i, url in enumerate(PAGES_TO_SCRAPE):
        slug = url.rstrip("/").split("/")[-1][:60]
        scrape_page(url, f"page_{i}_{slug}.txt")
        time.sleep(1)  # be polite to their server, don't hammer it