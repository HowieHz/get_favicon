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
        url = url.removeprefix('https://').removeprefix('http://')  # link形式 aaa.com
        r: requests.Response = requests.get(f'https://api.iowen.cn/favicon/{url}.png')
        return r.content, 'png', 'binary'