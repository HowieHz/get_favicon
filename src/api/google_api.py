import requests
from api.api_interface import APIBase
from typing import Union

class API(APIBase):
    @staticmethod
    def get(url: str) -> tuple[Union[str, bytes], str, str]:
        """api规范

        Args:
            url (str): [http://,https://]aaa.com

        Returns:
            tuple[Union[str, bytes], str, str]: 需要写入文件的值，文件后缀，写入模式('binary' / 'text')
        """
        r: requests.Response = requests.get(f'http://www.google.com/s2/favicons?domain={url}')
        return r.content, 'png', 'binary'