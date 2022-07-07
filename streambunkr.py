from requests_html import HTMLSession
import requests
import json

class StreamBunkr:

    chunk_size = 8388608

    def __init__(self, albumLink):
        self.session = HTMLSession()
        self.albumLink = albumLink

    def getLinks(self):
        self.links = {}
        response = self.session.get(url = self.albumLink).html.text
        response = response.split('\n')[-1]
        response = json.loads(response)['props']['pageProps']['files']
        for item in response:
            response = self.session.get(url = f"https://stream.bunkr.is/v/{item['name']}").html.text
            response = response.split("\n")[-1]
            response = json.loads(response)['props']['pageProps']['file']
            link = f"{response['mediafiles']}/{response['name']}"
            self.links[response['name']] = link
            # print()
        print(self.links)

    def dlLinks(self):
        for key in self.links:
            print(f"Downloading file {key}")
            response = requests.get(url = self.links[key], stream= True)
            with open(f"{key}", 'wb') as f:
                for chunk in response.iter_content(chunk_size= self.chunk_size):
                    f.write(chunk)

    @classmethod
    def getAlbumUrl(cls, _filename):
        url = next(cls.parseData(_filename))
        return cls(url)

    @staticmethod
    def parseData(_filename: str):
        with open (f'{_filename}', 'r') as f:
            for line in f.readlines():
                yield line.strip('\n').split('=')[-1]
    

sb = StreamBunkr.getAlbumUrl('DownloadLink.txt')
sb.getLinks()
sb.dlLinks()
