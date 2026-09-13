import requests
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (student project - WCE college assistant)"}
NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def get_urls_from_sitemap(sitemap_url):
    resp = requests.get(sitemap_url, headers=HEADERS, timeout=10, verify=False)
    root = ET.fromstring(resp.content)
    return [url.find("ns:loc", NS).text for url in root.findall("ns:url", NS)]

if __name__ == "__main__":
    page_urls_1 = get_urls_from_sitemap("https://walchandsangli.ac.in/page-sitemap1.xml")
    page_urls_2 = get_urls_from_sitemap("https://walchandsangli.ac.in/page-sitemap2.xml")
    all_pages = page_urls_1 + page_urls_2

    print(f"Found {len(all_pages)} total pages\n")
    for u in all_pages:
        print(u)