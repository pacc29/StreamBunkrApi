from requests_html import HTMLSession
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import json

class Bunkr:

    chunk_size = 10240

    def __init__(
        self,
        albumUrl,
        backoffFactor = 1,
        connect = 15,
        read = 15,
        timeout = 15
    ):
        self.htmlSession = HTMLSession()
        self.albumUrl = albumUrl
        self.failedDownload = []
        self.timeout = timeout
        retry = Retry(
            status_forcelist = [404, 429, 500, 502, 503, 504],
            allowed_methods = ["HEAD", "GET", "OPTIONS", "PUT", "DELETE", "POST"],
            backoff_factor= backoffFactor,
            connect = connect,
            read = read,
            total = connect + read
        )
        adapter = HTTPAdapter(max_retries = retry)
        self.htmlSession.mount('https://', adapter); self.htmlSession.mount('http://', adapter)   

    def getUrls(self):
        count = 0
        response = self.htmlSession.get(url = self.albumUrl).html.text
        response = response.split('\n')[-1]
        response = json.loads(response)['props']['pageProps']['album']['files']
        for item in response:
            try:
                url = self.htmlSession.get(url = f"""{item['cdn']}/{item['name']}""", allow_redirects = 3, timeout = self.timeout).url
                directUrl = json.loads(self.htmlSession.get(url = url).html.text.split("\n")[-1])['props']['pageProps']['file']
                self.downloadFile(f"{directUrl['mediafiles']}/{directUrl['name']}")
                count += 1
            except:
                pass
        print(f"{count} files downloaded")    

    def downloadFile(self, url):
        try:
            name = url.split('/')[-1]
            print(f"Trying to download {name}...  ")
            response = self.htmlSession.get(url = url, stream = True, timeout = self.timeout)
            print(response.status_code)
            if(response.status_code == 200):
                with open(name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size = self.chunk_size):
                        f.write(chunk)
            else:
                print(f"Error code: {response.status_code}")
                self.failedDownload.append(url)
        except:
            print('Unknown error exception')
            self.failedDownload.append(url)

    @classmethod
    def getAlbumUrl(cls, fileName):
        url = next(cls.parseData(fileName))
        return cls(url)

    @staticmethod
    def parseData(fileName: str):
        with open (f'{fileName}', 'r') as f:
            for line in f.readlines():
                yield line.strip('\n').split('=')[-1]


bunkr = Bunkr.getAlbumUrl('DownloadLink.txt')
bunkr.getUrls()