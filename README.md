# 自动获取网站favicon

The script is used to automatically get the favicon  
这个脚本是用于自动获取网站favicon的

建站后我将博客收藏夹转化为[我的博客](https://howiehz.top/links)的单向友链时，需要获取网站的favicon，因为一个个获取太累了（不够优雅），所以我就写了一个脚本来快捷获取

## 使用说明

1. 通过二进制文件运行  
    在[releases](https://github.com/HowieHz/get_favicon/releases)获取最新的二进制文件

2. 通过源码运行  
    下载python版本应>3.10  
    下载最新源码  
    运行脚本`src/main.py`  

第一次运行会在运行所在目录下生成links.txt,在其中放置你要获取favicon的网站
以下形式都是允许的:

```txt
https://howiehz.top
howiehz.top
https://howiehz.top/
howiehz.top/
```

之后按照提示继续执行，即可完成favicon下载

## 反馈

如有建议，添加api申请或其他讨论请进入项目[issue](https://github.com/HowieHz/get_favicon/issues)

## 一些可能出现的问题

Q：我的文件无法查看  
A：可能是无法从此api中获得该网站的favicon。如果文件大小不是特别小（比如217字节），ico后缀的文件可以尝试改为png后缀查看，png后缀的文件可以尝试改为ico后缀查看。
