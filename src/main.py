import requests, os, ssl
from typing import Union
from api import api_interface, append_char_api, getfavicon_api, google_api, html_parser_api, iowen_api

version = 'v1.1.0'

print(f'自动下载favicon工具 版本{version}')

links_file_path = './links.txt'
if not os.path.exists(links_file_path): # 初始化文件
    open(f"{links_file_path}",'w')
    input('''
请在该脚本执行目录下的links.txt文件内填入你需要获取favicon的网站的链接，一行一个
例:
a.com (请确保a.com可使用https://a.com访问)
a.com/ (请确保a.com/可使用https://a.com/访问)
http://a.com
https://a.com
http://a.com/
https://a.com/

填写完毕后回车
''')

default_dir_path: str = './favicons/'
raw_dir_path = input(f"输入保存目录，最后一个字符如果不是 / 会自动添加，不输入直接回车即为默认，默认位置为 {default_dir_path} :")
if raw_dir_path:
    dir_path: str = f"{raw_dir_path.removesuffix('/')}/"
else:
    dir_path: str = default_dir_path

choice_api: str = input('''
使用哪个api
请输入0后回车 使用getFavicon api （请确保可以通畅的连接http://www.getfavicon.org） 
请输入1后回车 使用google api（16*16 png）（请确保可以通畅的连接http://www.google.com）
请输入2后回车 直接在链接最后加上/favicon.ico获取
请输入3后回车 使用iowen api （介绍 https://www.iowen.cn/faviconwangzhantubiaozhuaquapijiekou/） 
请输入4后回车 下载该页面的html文件，并分析其<link rel="icon">和<link rel="shortcut icon">标签（主要适用于上面的api下载的icon和实际的icon不同的情况）
（此处4号api失败可以尝试2号api）(实测除2，4api以外，0号api速度和质量都较好)
默认为4:''')

if not os.path.exists(dir_path): # 初始化文件夹
    os.makedirs(dir_path)
    
with open('./links.txt') as links_file_stream: #读取links.txt
    for link in links_file_stream.readlines():  
        if link.startswith("#"): # 开头#跳过这条链接
            continue

        link: str = link.removesuffix('\n').removesuffix('/') # 去除末尾换行符和可能的/
        if not link.startswith('https://') and not link.startswith('http://'):  # 给没有https://也没有http://的链接加上https://
            link = f'https://{link}'
        
        ico_file_name = link.replace('/','_').replace(':','_').replace('___','_')   # 处理文件名
        # link形式 [http://,https://]aaa.com

        print(f'正在下载 {link} 的图标')
        file_type: str = 'png'
        api: api_interface.APIBase = None
        writing_mode: str = 'binary'
        content: Union[str, bytes] = None
        match choice_api:
            case '0':
                api = getfavicon_api.API
            case '1':
                api = google_api.API
            case '2':
                api = append_char_api.API
            case '3':
                api = iowen_api.API
            case _:
                api = html_parser_api.API

        try:
            content, file_type, writing_mode = api.get(link)
            ico_file_name: str = f"{ico_file_name}.{file_type}"  # 处理文件名
            
            # 保存文件
            if writing_mode == 'binary':
                with open(f"{dir_path}{ico_file_name}","wb") as ico_file_stream:
                    ico_file_stream.write(content)
            elif writing_mode in ('txt', 'text'):
                with open(f"{dir_path}{ico_file_name}","w", encoding='utf-8') as ico_file_stream:
                    ico_file_stream.write(content)
            else:
                ...
        except (ssl.SSLEOFError, requests.exceptions.SSLError):
            print("网络异常，请重新获取此链接的图标")
        print(f'已保存到 {dir_path}{ico_file_name}')

input('完成图标下载，按回车结束程序 （如有问题，请进入 https://github.com/HowieHz/get_favicon/issues 反馈）')