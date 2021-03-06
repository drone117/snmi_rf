import re
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import ssl

from urllib.request import urlopen

ssl.match_hostname = lambda cert, hostname: True
# domain_rf = u'http://снми.рф/архив'
# domain = domain_rf.encode('idna')
class fetcher():
    @staticmethod
    def fetch_data():
        latest_news_dict = {}
        latest_news_head = ''
        archive_url = "https://xn--h1ahcp.xn--p1ai/%D0%B0%D1%80%D1%85%D0%B8%D0%B2/"
        archive_page = urlopen(archive_url)
        archive_html = archive_page.read().decode("utf-8")
        archive_pattern = "news.*?href=.*?>"
        archive_match_pattern = re.search(archive_pattern, archive_html, re.IGNORECASE)
        archive_match_months = archive_match_pattern.group()
        archive_match_months = re.sub("<.*?>", "", archive_match_months)
        latest_match_first = archive_match_months.find("https")
        latest_news = archive_match_months[latest_match_first:]
        latest_match_latest = latest_news.find(">")
        latest_news_url = latest_news[:latest_match_latest - 1]
        latest_news_page = urlopen(latest_news_url)
        latest_news_html = latest_news_page.read().decode("utf-8")
        soup_latest = BeautifulSoup(latest_news_html, "html.parser")
        for tags in soup_latest.find_all(["h2", "p"]):
            if tags.name == 'h2':
                latest_news_head = '*' + tags.text + '*'
                latest_news_dict[latest_news_head] = ''
            else:
                latest_news_dict[latest_news_head] = latest_news_dict[latest_news_head] + tags.text + ' '
        return latest_news_dict

    @staticmethod
    def fetch_date():
        archive_url = "https://xn--h1ahcp.xn--p1ai/%D0%B0%D1%80%D1%85%D0%B8%D0%B2/"
        archive_page = urlopen(archive_url)
        archive_html = archive_page.read().decode("utf-8")
        archive_pattern = "news.*?href=.*?>"
        archive_match_pattern = re.search(archive_pattern, archive_html, re.IGNORECASE)
        archive_match_months = archive_match_pattern.group()
        archive_match_months = re.sub("<.*?>", "", archive_match_months)
        latest_match_first = archive_match_months.find("https")
        latest_news = archive_match_months[latest_match_first:]
        latest_match_latest = latest_news.find(">")
        latest_news_url = latest_news[:latest_match_latest - 1]
        latest_news_page = urlopen(latest_news_url)
        latest_news_html = latest_news_page.read().decode("utf-8")
        soup_latest = BeautifulSoup(latest_news_html, "html.parser")
        latest_date = soup_latest.find('div', class_="paper__date date").text
        latest_date = latest_date.strip().replace("\n", "").replace("  ", " ")
        latest_news_text = f'Дайджест от {latest_date}' + '\n'
        return latest_news_text

