# forked from linenotipy
# https://pypi.org/project/linenotipy/
import os
import requests
import io

class Line:
    def __init__(self, *, token):
        self.url = "https://notify-api.line.me/api/notify"
        self.headers = {"Authorization": "Bearer " + token}

    def post(self, **kwargs):
        files = kwargs.get("imageFile", None)
        if files is not None:
            files = {"imageFile": open(kwargs["imageFile"], "rb")}
        return requests.post(
            self.url, headers=self.headers, params=kwargs, files=files
        ).json()

    def post_raw_image(self, **kwargs):
        raw_image = kwargs.get("raw_image", None)
        if raw_image is not None:
            bytesio = io.BytesIO(raw_image)
            files = {"imageFile": bytesio.read()}
            kwargs.pop('raw_image')
        return requests.post(
            self.url, headers=self.headers, params=kwargs, files=files
        ).json()

    def post_image_by_url(self, **kwargs):
        image_url = kwargs.get("image_url", None)
        if image_url is not None:
            files = {"imageFile": self.retrieve_byte_image(image_url)}
        return requests.post(
            self.url, headers=self.headers, params=kwargs, files=files
        ).json()

    def retrieve_byte_image(self, url):
        return requests.get(url, stream=True).content


if __name__ == '__main__':
    from raw_image import raw_image
    from dotenv import load_dotenv
    load_dotenv()

    l = Line(token=os.getenv('LINE_TOKEN'))
    url = "https://docs.python.org/ja/3/_static/py.png"
    raw_image = requests.get(url, stream=True).content
    print(raw_image)
    l.post_image_by_url(message='test', image_url=url)
    l.post_raw_image(message='test.jpg', raw_image=raw_image)

    print('done')
