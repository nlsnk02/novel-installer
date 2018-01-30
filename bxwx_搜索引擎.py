#coding=utf-8
import sys 
import re
from bs4 import BeautifulSoup
#import multiprocessing as mp
import multiprocessing.dummy as mp
import requests
import time

def log ():
    while 1:
        time.sleep(5)
        if slend:
            break
        print (bxwx_dl)

def iget (url,*args, **kwds):
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    with requests.get(url,headers = header,*args, **kwds) as f:
        return f.content

def imap (func,lst,sum=40):
    pool = mp.Pool(sum)
    return pool.map(func,lst)
    
###笔下文学的下载
def bxwx_a_page(i):
    global bxwx_dl
    for cs in range(3):
        try:
            text = iget('http://bxwx.com' +i['href'], timeout=30).decode('gb2312','replace')
            html = BeautifulSoup(text, 'lxml')
            strs = html.find('div',{'id' :'BookText'}).get_text()
            break
        except (UnicodeDecodeError,requests.exceptions.ConnectTimeout) as err:
            #AttributeError,
            print('出错', err, i['href'])
            strs = i['href']+'该章下载失败'
            break
        except:
            print(i['href'] + '出现未知错误,开始循环')
    if cs == 2:
        strs = i['href']+'该章下载失败'
    if  0<cs<2:
        print(i['href']+'de错误以解决')
    bxwx_dl += 1
    return ''.join(strs.split())

def bxwx_search (n): #搜索小说
    name = requests.utils.quote(n.encode('gb2312'))
    html = BeautifulSoup(iget('http://www.bxwx.com/modules/article/search.php?searchkey='
                                + name).decode('gb2312'), 'lxml')
    print('搜索完毕')
    if html.find('a', {'class' : 'viewalllinks'}):
        #print(html)
        return html.find('a', {'class' : 'viewalllinks'})['href']
    else:
        return more_novel(html)[1][1][1]

def more_novel (html):#将多本小说变成列表
    trs = html.findAll('tr')
    def foo (tr):
        lst = []
        for i in tr.findAll(('th','td')):
            content = [i.get_text()]
            try:
                content.append(i.find('a')['href'])
            except:
                content.append(None)
            lst.append(content)
        return lst
    return [foo(i) for i in trs]
    
    
def  bxwx_main (url): #拉取一本小说全部页面的url
    page = BeautifulSoup(iget(url).decode('gb2312',), 'lxml')
    print('read_main')
    return (page.findAll('a', {'href' : re.compile(r'/\d/\d*/\d*\.html')}))
    
def bxwx ():
    res = bxwx_main(bxwx_search('斗罗大陆'))
    return imap(bxwx_a_page,res) 

if __name__ == '__main__':
    bxwx_dl = 0
    slend = None
    print('函数加载完毕')
    sys.setrecursionlimit(100000000)
    #打开日志
    mp.Process(target=log).start()
    #下载小说
    res = bxwx()
    print('ok==>',bxwx_dl)
    slend = True
    with open ('a.txt','w') as f:
        for i in res:
            if not(i == None):
                f.write(i+'\n')
    print('下载完成')
