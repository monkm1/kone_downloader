# coding: utf8
# title: 코네 사이트 추가
# comment: https://kone.gg
# author: monkm1

import re

import clf2
import downloader
import errors
import requests
from utils import Downloader, File, Session, Soup, clean_title

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


class LoginRequired(errors.LoginRequired):
    def __init__(self, *args):
        super().__init__(*args, method="browser", url="https://kone.gg/account/signin")


class Downloader_kone(Downloader):
    type = "kone"
    URLS = ["kone.gg"]
    user_agent = USER_AGENT
    ACCEPT_COOKIES = [r"(.*\.)?kone\.gg"]
    _soup = None
    icon = "https://kone.gg/favicon.ico"

    def init(self):
        self.session = Session()

    @property
    def soup(self):
        if self._soup is None:
            html = clf2.solve(self.url, session=self.session)["html"]
            self._soup = Soup(html)
            nsfwcontent = self._soup.find("h1", class_="text-2xl font-bold")

            if nsfwcontent and "민감한 콘텐츠" in nsfwcontent.text:
                raise LoginRequired()
        return self._soup

    def read(self):
        title = self.soup.find("title").text
        pattern = r"^(.*) - .*? \| 코네$"
        match = re.search(pattern, title)

        if match:
            title = match.group(1).strip()

        self.title = clean_title(title)

        self.urls = get_imgs(self.soup)


def get_imgs(soup):

    def check_article_classes(tag):
        return tag.name == "div" and tag.has_attr("class") and "relative" in tag["class"] and "min-h-60" in tag["class"]

    article = soup.find(check_article_classes)

    targets = article.findAll("img")

    results = []
    for target in targets:
        url = target["src"]
        """
        respone = requests.head(url, headers={"User-Agent": USER_AGENT})

        if respone.status_code == 200:
            contenttype = respone.headers.get("Content-Type")
            if contenttype:
                if contenttype == "image/jpeg":
                    ext = "jpg"
                elif contenttype == "image/svg+xml":
                    ext = "svg"
                else:
                    ext = contenttype.split("/")[-1]
            else:
                ext = "jpg"
        else:
            ext = "jpg"
        """
        ext = "webp"
        filename = f"{len(results):04}.{ext}"
        results.append(File({"url": url, "name": filename}))

    return results
