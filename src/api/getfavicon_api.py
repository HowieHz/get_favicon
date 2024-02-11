import requests
from api.api_interface import APIBase
from typing import Union

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0"
}

class API(APIBase):
    @staticmethod
    def get(url: str) -> tuple[Union[str, bytes], str, str]:
        """api规范

        Args:
            url (str): [http://,https://]aaa.com

        Returns:
            tuple[Union[str, bytes], str, str]: 需要写入文件的值，文件后缀，写入模式('binary' / 'text')
        """
        r: requests.Response = requests.get(f'http://www.getfavicon.org/get.pl?url={url}&submitget=get+favicon', headers=headers)  # f'http://www.getfavicon.org/?url={link}/favicon.png')
        return r.content, 'ico', 'binary'