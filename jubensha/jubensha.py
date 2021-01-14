import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jubensha.settings")   #这里的pga_lord就是你的项目名称
django.setup()

from selenium import webdriver
import re
import time
import pymysql

a = []#储存<h3>
b = []#存储链接
c = []#存储标题
d = []#存储上传时间
e = [] #存储公众号标题




#打开网页
def _open_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


#找出网页对应的所有代码,我们可以发现我们所需要的链接和标题都在<h3>标签里面
def _daima_url(driver):
    html=driver.page_source
    for match in re.finditer(r'<h3>[\s\S]*?</h3>', html):
        a.append(match.group(0))
    return a


def _lianjie(a):
    b.clear()
    #开始抽取连接
    for i in a:
        match = re.findall(r'href="[\s\S]*?"', i)
        '''
        这是我们用正则表达式抽取的其中一个连接
href="/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS06-5IhBS2ypDMr6FGtLFbgWcsctcYPvKVqXa8Fplpd9oRXssJ58
mZGUQVFWFookiKQvBqtegTY961Ds0mJLtisO3FNI8YrIhSAZGufEp77n6BJYxuyFBPUMXKnnftaUwRz4GLrWWxnHzadcxZNQu6G_wFHoYLjAOgQOZRUWnvgC
hAjrMkiIHxmQIbR9d7npNyCnwmo3nebp34_2VoRHjPvf3q8uRDTfkw..&amp;type=2&amp;query=%E5%89%A7%E6%9C%AC%E6%9D%80&amp;token=59E3
71874D08B6CBBCBE0478AE674B26BC0EEA255FFEA11C"

这是网站上的正确网页连接：
https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS5CrUICkq2XgSxRFYvNrd_TYhAVFkqj_B
FqXa8Fplpd9-xgO1y3TuduWEUs87NyuYj4_eDZMOaLpw9PcP4ntx1Pzy3429yQF-CwyKxf3MWFbh6nyH6zDAE4XEq9BjOpF8Vv76Naae5UD7Drys-s0C_GIS
WxrNqBQdurhvf9i7Lo1itwe-h74-j6D1WE3zAXzMB_lWL5Da00MD9FJxbj4C2f2CsG6-xMgzQ..&amp;type=2&amp;query=%E5%89%A7%E6%9C%AC%E6%9
D%80&amp;token=4D51374531DD239CE4E65C4E117C4DCDE4C87B105FFD0C57

可以看出对比正确的连接其中有 amp 与正确的连接不同
所欲我们要在开头加个https://weixin.sogou.com 以及把href= 和amp用replace替换掉
'''
    # 清除href=" str(match[0]) 解释 因为match变量是一个列表 无法进行下一个正则匹配 我们要吧里面内容全部换成str类型才能匹配下一个正则

        result = re.sub('href="', "", str(match[0]))
    #清除amp;
        result2 = re.sub("amp;", "", result)
    #现在我们将正确连接储存到b中
        b.append('https://weixin.sogou.com'+result2)
    return b



def _biaoti(a):
    c.clear()
    for i in a:
        result = re.findall(r"uigs=[\s\S]*?</a>", i)
        '''uigs="article_title_0"><em><!--red_beg-->剧本杀<!--red_end--></em>是不是一门好生意?</a>\n</h3>
           我们要去掉结果中的1.uigs="article_title_0">
                         2. <em><!--red_beg-->
                         3.!--red_end--></em>
        '''
        #1.去除uigs=
        result1 = re.sub(r"uigs=[\S\s]*?>", "", str(result[0]))
        #2.去除<em><!--red_beg-->
        result2 = re.sub("<em><!--red_beg-->", "", result1)
        #3.去除!--red_end--></em>
        result3 = re.sub("<!--red_end--></em>", "", result2)

        result4 = re.sub("</a>", "", result3)
        #我们将正确的标题存储到c中
        c.append(result4)
    return c


#上传时间

def _shangchuantime(driver):
    #可以根据元素看起来上传时间都保存在class=“s2”的标签中 我们用selenium中的CSS查找元素找出所有的class=“s2”的元素并用for循环保存每一个
    #element.get_attribute('outerHTML') 是网页的源代码
    elements = driver.find_elements_by_css_selector('.s2')
    for element in elements:
        #<span class="s2"><script>document.write(timeConvert('1604116776'))</script>2020-11-29</span>
        #这是其中的一条 我们用找标题的方法将2020-11-29找出来
        result = re.findall(r"</script>[\S\s]*?<", element.get_attribute('outerHTML'))
        result1 = re.sub("</script>", "", str(result[0]))
        result2 = re.sub("<", "", result1)
        d.append(result2)
    return d



def _GZHtitle(driver):
    elements = driver.find_elements_by_css_selector('.account')
    ''''<h3>\n<a target="_blank" href="/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS06-5IhBS2ypDMr6FGt
    LFbgWcsctcYPvKVqXa8Fplpd9oRXssJ58mZGUQVFWFookiKQvBqtegTY961Ds0mJLtisO3FNI8YrIhSAZGufEp77n6BJYxuyFBPUMXKnnftaUwRz4GLr
    WWxnHzadcxZNQu6G_wFHoYLjAOgQOZRUWnvgChAjrMkiIHxmQIbR9d7npNyCnwmo3nebp34_2VoRHjPvf3q8uRDTfkw..&amp;type=2&amp;query=%
    E5%89%A7%E6%9C%AC%E6%9D%80&amp;token=59E371874D08B6CBBCBE0478AE674B26BC0EEA255FFEA11C" id="sogou_vr_11002601_title_0
    " uigs="article_title_0"><em><!--red_beg-->剧本杀<!--red_end--></em>是不是一门好生意?</a>\n</h3>', '''

    #按照上述方法把标题找出来
    for element in elements:
        result0 = re.findall(r"uigs=[\S\s]*?<", element.get_attribute('outerHTML'))
        result1 = re.sub("</script>", "", str(result0[0]))
        result2 = re.sub(r"uigs=[\S\s]*?>", "", result1)
        result3 = re.sub("<", "", result2)
        e.append(result3)
    return e







def chucun(driver):
    a = _daima_url(driver)
    b = _lianjie(a) #结束后所有连接在b中
    c = _biaoti(a) #结束后所有标题在c中
    d = _shangchuantime(driver) #结束后所有上传时间在d中
    e = _GZHtitle(driver) #结束后所有公众号标题在e中


def zhixing():
    url = 'https://weixin.sogou.com/weixin?type=2&query=%E5%89%A7%E6%9C%AC%E6%9D%80&ie=utf8&s_from=input&_sug_=y&_sug_type_='
    for k in range(5):
        driver = _open_url(url)
        chucun(driver)
        # 我们找到下一页的连接
        next_daima = driver.find_element_by_id("sogou_next")
        # 下一页连接的源代码
        next_url0 = re.search(r"href[\s\S]*?class", next_daima.get_attribute('outerHTML'))
        # 取出连接
        next_url1 = next_url0.group(0).replace('href="', "")
        next_url2 = 'https://weixin.sogou.com/weixin' + next_url1.replace('class', '')
        url = next_url2.replace('amp;', '')
        time.sleep(3)

#使用print检查数据有没有问题
#执行完第八个函数之后 我们可以在后面打赢出来abcde里面的内容以及数据数有没有出错，方便存储到数据库中的内容不会出错
if __name__ == "__main__":
    zhixing()

    print(b)
    print(c)
    print(d)
    print(e)

    print(len(b))
    print(len(c))
    print(len(d))
    print(len(e))
#将数据储存到数据库中 ：
    for i in range(50):
        user = jubensha(bt=c[i],lj=b[i],sj=d[i],gzh=e[i])
        user.save()



