import requests
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (student project - WCE college assistant)"}
NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def get_urls_from_sitemap(sitemap_url):
    resp = requests.get(sitemap_url, headers=HEADERS, timeout=10, verify=False)
    root = ET.fromstring(resp.content)
    urls = [url.find("ns:loc", NS).text for url in root.findall("ns:url", NS)]
    return urls

if __name__ == "__main__":
    notice_urls = get_urls_from_sitemap("https://walchandsangli.ac.in/notice_board-sitemap.xml")
    print(f"Found {len(notice_urls)} notice URLs")
    for u in notice_urls[:10]:
        print(u)