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
            return parser.ret[-1]
            # 要是这个网站写了多条<link rel="icon">和<link rel="shortcut icon">标签, 
            # 就会多次解析，后面一条会覆盖前一条，最后留下的是最下面一条，也符合浏览器的读取，缺点是会多次下载该网站的icon
            # 实例：看到多个个网站高分辨率的写在低分辨率的后面
            #TODO 但是实际上浏览器加载的是第一条，所以是否要增加两个api，一个获取全部文件，一个“真”模拟浏览器获取第一个
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]):
        """解析思路
        1. 检查<link rel="icon">和<link rel="shortcut icon">标签
        2. 检查是否有type，有type的进入2.x流程
        2.1. 对应type除了svg都一定是二进制流直接下载，结束流程
        2.2. type是svg的，检查下href是不是.svg后缀，是说明是二进制流，不是说明是RFC2397定义的文本编码成base64的形式，直接下载，结束流程
        2.3. type不合法，调用检查href的流程（即3.x)
        3. 检查是否有href，没type有href的进入3.x流程
        3.1. 检查是否是RFC2397定义的一些数据（除开svg，因为svg用这个是要用文本模式写，其他都二进制流模式写就好了，还有svg必有type，况且前面已经处理过了）  #TODO 需要实验，没有type,svg在RFC2397和*.svg两种情况下是否能顺利读取，如果能顺利读取，那就要加上svg在这里了
        3.2. 检查href文件后缀（除去svg，因为前面处理过了），对应的直接二进制流模式写入  
        3- 只要有type或者href，就不走下面的流程了
        4. 有这标签，但是type和href属性都没有，那直接忽略掉了，置空
        
        实验数据：有没有type，type错误，不影响edge正确读取*.png和RFC2397的文件
        #TODO 故此提议是否应修改解析流程，先href再type
        #TODO 有type，但是是base64的数据呢，直接二进制写入了，不行的

        Args:
            tag (str): _description_
            attrs (list[tuple[str, str]]): _description_
        """
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
        
        # 无type，href也不合法，放弃掉，置空
    
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
                if 'href' in attr_value_dict:  # 不合法的type
                    self.href_attr_parser(href_value)
        return
