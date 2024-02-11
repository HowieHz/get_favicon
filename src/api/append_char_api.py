import requests
from api.api_interface import APIBase
from typing import Union

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0"
}

class API(APIBase):
    @staticmethod
    def get(url: str, browser_emulation_api_flag:bool = False) -> tuple[Union[str, bytes], str, str]:
        """api规范

        Args:
            url (str): [http://,https://]aaa.com
            browser_emulation_api_flag (bool): 如果是通过模拟浏览器api调用的api，这个flag为True

        Returns:
            tuple[Union[str, bytes], str, str]: 需要写入文件的值，文件后缀，写入模式('binary' / 'text')
        """
        r: requests.Response = requests.get(url=f'{url}/favicon.ico', headers=headers)
        content: bytes = r.content
        
        if not r.encoding:  # r.encoding是None那多半不是html文件了
            return content, 'ico', 'binary'

        print(r.encoding)
        content_str: str = content.decode(r.encoding)

        for line in content_str.splitlines():
            if not line: continue # 空行跳过

            if line=='<!DOCTYPE html>':
                if browser_emulation_api_flag:
                    return f'该网站无可用favicon\n如您使用实际访问该网站 {url} 有favicon\n请向该项目提出issue: https://github.com/HowieHz/get_favicon/issues/new \n或使用邮箱与作者联系，也可以选择加入讨论群反馈，感谢您的支持', 'txt', 'text'
                return f'{url} 无法使用此api获取favicon', 'txt', 'text'
            else:
                break  # 第一个有内容的行不是<!DOCTYPE html>那就不是html文件了
        
        return content, 'ico', 'binary'
