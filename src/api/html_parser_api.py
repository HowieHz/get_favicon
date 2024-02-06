from html.parser import HTMLParser
import urllib.parse
import requests
from api.api_interface import APIBase
from typing import Union

class API(APIBase):
    @staticmethod
    def get(url: str) -> tuple[Union[str, bytes], str, str]:
        """api规范

        Args:
            url (str): 

        Returns:
            tuple[Union[str, bytes], str, str]: 需要写入文件的值，文件后缀，写入模式('binary' / 'text')
        """
        response: requests.Response = requests.get(url)
        parser = HTMLParser(url=url)
        parser.feed(response.text)
        if parser.ret:
            return parser.ret[0]
        else:
            return (f'此api不支持该网站\nhtml原文:\n{response.text}', 'txt', 'txt')


class HTMLParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True, url=''):
        """Initialize and reset this instance.

        If convert_charrefs is True (the default), all character references
        are automatically converted to the corresponding Unicode characters.
        """
        self.url = url
        self.ret = []
        self.convert_charrefs = convert_charrefs
        self.reset()
    
    def get_binary_img(self, href_value: str, file_type: str):
        if not href_value.startswith('/'):
            href_value = f'/{href_value}'
        r: requests.Response = requests.get(f'{self.url}{href_value}')
        self.ret.append((r.content, file_type, 'binary'))

    def handle_starttag(self, tag, attrs):
        if tag == 'link':

            attr_value_dict: dict[str, str] = {}
            for attr_name, attr_value in attrs:
                attr_value_dict[attr_name] = attr_value

            if attr_value_dict['rel'] == 'icon' or attr_value_dict['rel'] == 'shortcut icon':  # 要是这个网站写了多条<link rel="icon">和<link rel="shortcut icon">标签, 就会多次解析，后面一条会覆盖前一条，最后留下的是最下面一条，也符合浏览器的读取，缺点是会多次下载该网站的icon
                # print('#45', attr_value_dict)
                if 'type' in attr_value_dict:
                    match attr_value_dict['type']:
                        case 'image/svg+xml':  # svg文件 https://developer.mozilla.org/zh-CN/docs/Web/Media/Formats/Image_types
                            self.ret.append((urllib.parse.unquote(attr_value_dict['href'].removeprefix('data:image/svg+xml,')), 'svg', 'txt'))
                        case 'image/apng': # apng
                            self.get_binary_img(attr_value_dict['href'], 'apng')
                        case 'image/avif': # avif
                            self.get_binary_img(attr_value_dict['href'], 'avif')
                        case 'image/gif': # gif
                            self.get_binary_img(attr_value_dict['href'], 'gif')
                        case 'image/jpeg': # .jpg, .jpeg, .jfif, .pjpeg, .pjp
                            self.get_binary_img(attr_value_dict['href'], 'jpeg')
                        case 'image/png': # .png
                            self.get_binary_img(attr_value_dict['href'], 'png')
                        case 'image/webp': # .webp
                            self.get_binary_img(attr_value_dict['href'], 'webp')
                        case 'image/bmp': # .bmp
                            self.get_binary_img(attr_value_dict['href'], 'bmp')
                        case 'image/x-icon': # .ico、.cur
                            self.get_binary_img(attr_value_dict['href'], 'ico')
                        case 'image/tiff': # .tif、.tiff
                            self.get_binary_img(attr_value_dict['href'], 'tif')
                        case _:
                            self.ret.append((f"如果看到此消息，请提交issue给此项目，包括此文件，开发者将很快进行适配\nself.url:{self.url}\nattr_value_dict['type']:{attr_value_dict['type']}", 'txt', 'txt'))  # 不合法的type，但是是合法的href，是否依然要下载，目前策略是放弃，需要进一步讨论，需要参考浏览器面对这种情况的应对策略
                elif 'href' in attr_value_dict:  # 没type属性，直接匹配href属性值的后缀
                    href_value = attr_value_dict['href']
                    file_type_list = ('jpg' ,'jpeg' , 'png', 'ico', 'webp', 'bmp', 'gif', 'cur', 'tif', 'tiff', 'jfif', 'pjpeg', 'pjp', 'avif', 'apng')
                    for file_type in file_type_list:
                        if href_value.endswith(f'.{file_type}'):
                            self.get_binary_img(href_value, file_type)
                            break
                    else:
                        ...  # 无type，href也不合法，目前策略是放弃，需要进一步讨论，需要参考浏览器面对这种情况的应对策略
                else:
                    ...  # 有<link rel="icon">和<link rel="shortcut icon">标签，但是没有href和type
