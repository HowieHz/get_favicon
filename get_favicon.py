import requests,os

version = 'v1.0.0'

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
默认为0:''')

if not os.path.exists(dir_path): # 初始化文件夹
    os.makedirs(dir_path)
    
with open('./links.txt') as links_file_stream: #读取links.txt
    for link in links_file_stream.readlines():  
        link: str = link.removesuffix('\n').removesuffix('/') # 去除末尾换行符和可能的/
        if not link.startswith('https://') and not link.startswith('http://'):
            link = f'https://{link}'
        
        ico_file_name = link.replace('/','_').replace(':','_').replace('___','_')   # 处理文件名
        # link形式 [http://,https://]aaa.com
        print(f'正在下载 {link} 的图标')
        match choice_api:
            case '1':
                ico_file_name: str = f"{ico_file_name}.favicon.png"  # 处理文件名
                r: requests.Response = requests.get(f'http://www.google.com/s2/favicons?domain={link}')
            case '2':
                ico_file_name: str = f"{ico_file_name}.favicon.ico"  # 处理文件名
                r: requests.Response = requests.get(f'{link}/favicon.ico')
            case '3':
                ico_file_name: str = f"{ico_file_name}.favicon.png"  # 处理文件名
                link = link.removeprefix('https://').removeprefix('http://')
                # link形式 aaa.com
                r: requests.Response = requests.get(f'https://api.iowen.cn/favicon/{link}.png')
            case _:
                ico_file_name: str = f"{ico_file_name}.favicon.ico"  # 处理文件名
                r: requests.Response = requests.get(f'http://www.getfavicon.org/get.pl?url={link}&submitget=get+favicon')
                # f'http://www.getfavicon.org/?url={link}/favicon.png')
        
        # 保存文件
        with open(f"{dir_path}{ico_file_name}","wb") as ico_file_stream:
            ico_file_stream.write(r.content)
        print(f'已保存到 {dir_path}{ico_file_name}')

input('完成图标下载，按回车结束程序 （如有问题，请进入 https://github.com/HowieHz/get_favicon/issues 反馈）')