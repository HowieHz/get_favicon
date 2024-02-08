from html.parser import HTMLParser
import urllib.parse
import requests
import base64
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
        response: requests.Response = requests.get(url=url, headers=headers)
        parser = HTMLParser(url=url)
        parser.feed(response.text)
        if parser.ret:
            return parser.ret[-1]  # 因为看到一个网站192*192写在32*32后面，所以取-1了
        else:
            return (f'此api不支持该网站\nhtml原文:\n{response.text}', 'txt', 'text')


class HTMLParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True, url=''):
        """Initialize and reset this instance.

        If convert_charrefs is True (the default), all character references
        are automatically converted to the corresponding Unicode characters.
        """
        self.convert_charrefs = convert_charrefs
        self.reset()
        
        # 新增
        self.url = url
        self.ret: list[Union[str,bytes], str, str] = []
    
    def get_binary_img(self, href_value: str, file_type: str):
        if href_value.startswith('//'):  # 处理一下 //xxx.xxx
            if self.url.startswith('https:'):
                href_value = 'https:' + href_value
            elif self.url.startswith('http:'):
                href_value = 'http:' + href_value
            # print(f"#gbi1 url={href_value}")
            r: requests.Response = requests.get(url=f'{href_value}', headers=headers)
        elif href_value.startswith('/'):  # 处理一下 /xxx.xxx
            # print(f"#gbi2 url={self.url.split('/')[0]}//{self.url.split('/')[2]}{href_value}")
            r: requests.Response = requests.get(url=f"{self.url.split('/')[0]}//{self.url.split('/')[2]}{href_value}", headers=headers)
        elif href_value.startswith('https:') or href_value.startswith('http:'):  # 处理一下 https://xxx.xxx or http://xxx.xxx
            # print(f"#gbi3 url={href_value}")
            r: requests.Response = requests.get(url=f'{href_value}', headers=headers)
        else:  # 处理一下 xxx.xxx
            # print(f"#gbi4 url={self.url.split('/')[0]}//{self.url.split('/')[2]}/{href_value}")
            r: requests.Response = requests.get(url=f"{self.url.split('/')[0]}//{self.url.split('/')[2]}/{href_value}", headers=headers)
        self.ret.append((r.content, file_type, 'binary'))
        return

    def handle_starttag(self, tag, attrs):
        # 要是这个网站写了多条<link rel="icon">和<link rel="shortcut icon">标签, 
        # 就会多次解析，后面一条会覆盖前一条，最后留下的是最下面一条，也符合浏览器的读取，缺点是会多次下载该网站的icon
        # 对应上面 return parser.ret[-1]
        if tag != 'link':
            return

        attr_value_dict: dict[str, str] = {}
        for attr_name, attr_value in attrs:
            attr_value_dict[attr_name] = attr_value

        if not (attr_value_dict['rel'] == 'icon') and \
            not (attr_value_dict['rel'] == 'shortcut icon'):  
            return
        
        # print('#45', attr_value_dict)
        
        href_value: str = attr_value_dict['href']
        if 'type' in attr_value_dict:
            self.type_attr_parser(href_value, attr_value_dict)
        elif 'href' in attr_value_dict:  
            self.href_attr_parser(href_value)
        else:
            pass # 有<link rel="icon">和<link rel="shortcut icon">标签，但是没有href和type
        
        return
    
    def href_attr_parser(self, href_value) -> None:
        # 先看看RFC2397定义的一些数据
        data_uri_scheme_dict: dict[str, str] = {
            "data:image/gif;base64,": "gif",
            "data:image/png;base64,": "png",
            "data:image/jpeg;base64,": "jpeg",
            "data:image/x-icon;base64,": "ico",
        }
        for data_uri_scheme in data_uri_scheme_dict.keys():
            if href_value.startswith(data_uri_scheme):
                self.ret.append((base64.b64decode(href_value.removeprefix(data_uri_scheme)), data_uri_scheme_dict[data_uri_scheme], 'binary'))
                return

        # 没type属性，也不符合RFC2397，直接匹配href属性值的后缀
        file_type_list = ('jpg' ,'jpeg' , 'png', 'ico', 'webp', 'bmp', 'gif', 'cur', 'tif', 'tiff', 'jfif', 'pjpeg', 'pjp', 'avif', 'apng')
        for file_type in file_type_list:
            if href_value.endswith(f'.{file_type}'):
                self.get_binary_img(href_value, file_type)
                return
        
        # 无type，href也不合法，目前策略是放弃，需要进一步讨论，需要参考浏览器面对这种情况的应对策略
    
    def type_attr_parser(self, href_value, attr_value_dict) -> None:
        match attr_value_dict['type']:
            case 'image/svg+xml':  # svg文件 https://developer.mozilla.org/zh-CN/docs/Web/Media/Formats/Image_types
                if not href_value.endswith('.svg'):
                    self.ret.append((urllib.parse.unquote(href_value.removeprefix('data:image/svg+xml,')), 'svg', 'text'))
                    return
                self.get_binary_img(href_value, 'svg')
            case 'image/apng': # apng
                self.get_binary_img(href_value, 'apng')
            case 'image/avif': # avif
                self.get_binary_img(href_value, 'avif')
            case 'image/gif': # gif
                self.get_binary_img(href_value, 'gif')
            case 'image/jpeg': # .jpg, .jpeg, .jfif, .pjpeg, .pjp
                self.get_binary_img(href_value, 'jpeg')
            case 'image/png': # .png
                self.get_binary_img(href_value, 'png')
            case 'image/webp': # .webp
                self.get_binary_img(href_value, 'webp')
            case 'image/bmp': # .bmp
                self.get_binary_img(href_value, 'bmp')
            case 'image/x-icon': # .ico、.cur
                self.get_binary_img(href_value, 'ico')
            case 'image/tiff': # .tif、.tiff
                self.get_binary_img(href_value, 'tif')
            case _:
                self.ret.append((f"该网站填写了错误的数据标签，如果看到此消息，请提交issue给此项目，包括此文件，开发者将帮忙联系网站管理者\nself.url:{self.url}\nattr_value_dict['type']:{attr_value_dict['type']}", 'txt', 'text'))  # 不合法的type
        return
