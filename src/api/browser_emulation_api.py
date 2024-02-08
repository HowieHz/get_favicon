import requests
from api.api_interface import APIBase
from typing import Union
from . import html_parser_api, append_char_api

class API(APIBase):
    @staticmethod
    def get(url: str) -> tuple[Union[str, bytes], str, str]:
        """api规范

        Args:
            url (str): [http://,https://]aaa.com

        Returns:
            tuple[Union[str, bytes], str, str]: 需要写入文件的值，文件后缀，写入模式('binary' / 'text' / 'txt')
        """
        ret = html_parser_api(url)
        if ret[1] == 'txt':
            ret = append_char_api(url)
        return ret
    