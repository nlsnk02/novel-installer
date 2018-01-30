#coding=utf-8
import sys 
import re
from bs4 import BeautifulSoup
import multiprocessing.dummy as mp
import requests
import time

def iget (url,*args, **kwds):
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    with requests.get(url,headers = header,*args, **kwds) as f:
        return f.content

def log ():
    while 1:
        time.sleep(5)
        if slend:
            break
        print ('已下载：',str(bxwx_dl))

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
            print(i['href'] + '出现错误,开始循环')
    if cs == 2:
        strs = i['href']+'该章下载失败'
        print(i['href']+'该章下载失败')
    if  0<cs<2:
        print(i['href']+'de错误以解决')
    bxwx_dl += 1
    return ''.join(strs.split())

def bxwx_search (n): #搜索小说
    def tb2lst (html):#将多本小说变成列表
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
    def smt_cos (lst):#让用户选择下载的小说
        def foo (*strs):
            while 1:
                res = input(*strs)
                try:
                    if (int(res)<1) or (int(res)>(len(arr)-1)):
                        return 1
                    else:
                        return int(res)
                except:
                    print('try a agin! you should tybe numbers, and this numbers should in the list.')
        print('有多本小说被搜索到：\n')
        arr = [(i[0][0], i[1][1]) for i in lst]
        [print(i[0],'<',n,'>') for n,i in enumerate(arr)]
        return arr[foo('选择需要下载的小说的<序号>')][1]
        
    name = requests.utils.quote(n.encode('gb2312'))
    html = BeautifulSoup(iget('http://www.bxwx.com/modules/article/search.php?searchkey='
                                + name).decode('gb2312'), 'lxml')
    print('搜索完毕')
    if html.find('a', {'class' : 'viewalllinks'}):
        #print(html)
        return html.find('a', {'class' : 'viewalllinks'})['href']
    else:
        return smt_cos(tb2lst(html))
    
def  bxwx_main (url): #拉取一本小说全部页面的url
    page = BeautifulSoup(iget(url).decode('gb2312',), 'lxml')
    print('read_main',page.find('h1').get_text())
    return (page.findAll('a', {'href' : re.compile(r'/\d/\d*/\d*\.html')}))
    
def bxwx (i):
    res = bxwx_main(bxwx_search(i))
    #打开日志
    mp.Process(target=log).start()
    return imap(bxwx_a_page,res) 

if __name__ == '__main__':
    bxwx_dl = 0
    slend = None
    print('函数加载完毕')
    sys.setrecursionlimit(100000000)
    name = input('请输入小说的名字：')
    #下载小说
    res = bxwx(name)
    print('ok==>',bxwx_dl)
    slend = True
    with open ('a.txt','w') as f:
        for i in res:
            if not(i == None):
                f.write(i+'\n')
    print('下载完成')
