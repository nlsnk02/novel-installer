#coding=utf-8
import sys 
import re
from bs4 import BeautifulSoup
import multiprocessing.dummy as mp
import requests
import time
import random

def nm_iget (url,encoding=('utf-8','replace'), *args, **kwds):
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
    with requests.get(url,headers = header,*args, **kwds) as f:
        if isinstance(encoding,tuple):
            return BeautifulSoup(f.content.decode(*encoding),'lxml')
        else:
            return BeautifulSoup(f.content.decode(encoding),'lxml')

def log ():
    global ip_list
    global log_dl
    global slend
    slend=None
    log_dl=0
    n=0
    ip_list =get_ip_list()
    while 1:
        n+=5
        time.sleep(5)
        if slend:
            break
        elif n > 20:
            ip_list =get_ip_list() +ip_list
            n=0
        print ('已下载：',log_dl)

def imap (func,lst,sum=40):
    pool = mp.Pool(sum)
    return pool.map(func,lst)

def ihelp ():
    print('''
    函数加载完毕。
    此下载器从笔下文学下载，该下载地址可能删除了一些老小说。
    添加会使下载变慢很多。（当然你也可以自己去网上买代理）
    其他搜索引擎正在陆续开发中。
    如果用mp3看书请将下载的小说编码改为ansi，应该懂吧。
    
    ''')

    
    
###基本代理函数
def get_ip_list():
    '''顺序：《‘’，‘’，国家（无），IP，端口，地址，匿名，类型，存活时间，验证时间，‘’》'''
    arr =[]
    for i in nm_iget('http://www.xicidaili.com/').find('table',{'id' : 'ip_list'}).findAll('tr'):
        arr.append(i.get_text().split('\n'))
    ip_list =[]
    for i in arr:
        if '分钟' in i[-2]:
            ip_list.append((i[6], i[2], i[-3]))
    return ip_list
    
def get_proxie(n,ip_list):
    http_list = [i for i in ip_list if i[0]==n]
    return http_list[random.randint(0,len(http_list)-1)]

def iget(url,*args,**kwargs):
    def t2d (*args):
        proxie = {}
        for res in args:
            ad = {res[0] : res[0]+'://' +res[1]}
            proxie.update(ad)
        return proxie
    
    global ip_list
    head = url.split(':')[0].upper()
    for _ in range(6):
        try:
            np=get_proxie(head,ip_list)
            return nm_iget(url,*args,proxies=t2d(np),**kwargs)
        except requests.exceptions.ProxyError as err:
            ip_list.remove(np)
            print('proxy_err')
   

 ###笔下文学的下载
def bxwx_a_page(i):
    global log_dl
    for cs in range(3):
        name =i
        try:
            html = iget('http://bxwx.com' +i['href'], ('gb2312','replace'), timeout=30)
            name=html.find('h1').get_text()
            strs = html.find('div',{'id' :'BookText'}).get_text()
            break
        except (UnicodeDecodeError,requests.exceptions.ConnectionError) as err:
            print('出错', err, i['href'])
            strs = i['href']+'该章下载失败'
            break
        except AttributeError as err:
            print(i['href'] + '小问题，不要担心')
    if  0<cs<2:
        print(i['href']+'de错误以解决')
    if cs == 2:
        strs = i['href']+'该章下载失败'
        print(i['href']+'该章下载失败')
    else:
        log_dl += 1
        return name+'\n'+(''.join(strs.split()))

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
                        print('这里可能没有你想要的书，关闭程序或再次输入')
                    else:
                        return int(res)
                except:
                    print('再次输入。你需要输入像   1   这样的数字')
        print('有多本小说被搜索到：\n')
        arr = [(i[0][0], i[1][1]) for i in lst]
        [print(i[0],'<',n,'>') for n,i in enumerate(arr)]
        return arr[foo('选择需要下载的小说的<序号>')][1]
        
    name = requests.utils.quote(n.encode('gb2312'))
    html = nm_iget('http://www.bxwx.com/modules/article/search.php?searchkey='
                                + name, ('gb2312', 'replace'))
    print('搜索完毕')
    if html.find('a', {'class' : 'viewalllinks'}):
        #print(html)
        return html.find('a', {'class' : 'viewalllinks'})['href']
    else:
        return smt_cos(tb2lst(html))
    
def  bxwx_main (url): #拉取一本小说全部页面的url
    def foo (n):
        return ''.join(list(n)[1:-5])
    global name
    page = nm_iget(url,'gb2312')
    name = foo(page.find('h1').get_text())
    res = page.findAll('a', {'href' : re.compile(r'/\d/\d*/\d*\.html')})
    print('read_main',name ,'共有',len(res),'章')
    return res
    
    
def bxwx (i):
    res = bxwx_main(bxwx_search(i))#获取全部小说章节列表
    mp.Process(target=log).start()#打开日志
    time.sleep(3)
    return imap(bxwx_a_page,res)#下载全部小说

if __name__ == '__main__':
    ihelp()
    sys.setrecursionlimit(100000000)
    name = input('请输入小说的名字：')
    #下载小说
    res = bxwx(name)
    print('ok==>',log_dl)
    slend = True
    with open (name+'.txt','w',encoding= 'utf-8') as f:
        for i in res:
            if not(i == None):
                f.write(i+'\n')
    print('下载完成')
