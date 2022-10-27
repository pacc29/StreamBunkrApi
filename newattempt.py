from urllib import response
from requests_html import HTMLSession
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import json

class Bunkr:

    chunk_size = 8388608

    def __init__(
        self,
        albumUrl,
        backoffFactor = 1,
        connect = 15,
        read = 15,
        timeout = 15
    ):
        self.session = HTMLSession()
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
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)   


    def getUrls(self):
        response = self.session.get(url = self.albumUrl).html.text
        response = response.split('\n')[-1]
        response = json.loads(response)['props']['pageProps']['album']['files']
        for item in response:
            url = self.session.get(url = f"{item['cdn']}/{item['name']}", allow_redirects = 3, timeout = self.timeout).url
            self.downloadFile(url)
            # self.urls.append(url) 

        # print(response)    

    def downloadFile(self, url):
        try:
            name = url.split('/')[-1]
            print(f"Trying to download {name}")
            # response = self.session.get(url = url, stream = True)
            # with open(name, 'wb') as f:
            #     for chunk in response.iter_content(chunk_size = self.chunk_size):
            #         f.write(chunk)


        except requests.exceptions.ConnectionError as e:
            self.failedDownload.append(url)
            print(e)
        except:
            self.failedDownload.append(url)
            print('Unknown error exception')


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