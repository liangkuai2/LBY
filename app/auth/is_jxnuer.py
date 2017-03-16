# -*- coding: utf-8 -*-
import requests
from flask import flash
from lxml import etree
from requests import ConnectionError

class is_jxnuer(object):
    def __init__(self,stu_id,password,type):
        self.id = str(stu_id)
        self.password = password
        self.type = type
        self.login_url = 'http://jwc.jxnu.edu.cn/Default_Login.aspx?preurl='
        self.cookies = ''


    def get_cookies(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.113 Safari/537.36'}
        data = {'__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '','__VIEWSTATE':'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','__EVENTVALIDATION':'/wEWSQLm7arZDALr6+/kCQK3yfbSBAKDspbeCQL21fViApC695MMAsjQmpEOAsjQpo4OAv3S2u0DAv3S9t4DAqPW8tMDAv3S6tEDAqPW3ugDArWVmJEHAr/R2u0DAqrwhf4KAsjQtoIOAuHY1soHAsjQooMOAv3S3ugDArfW7mMC/dL+0AMCvJDK9wsC/dLy0wMCr9GugA4C8pHSiQwC6dGugA4C+dHq0QMC3NH61QMCjtCenA4CntDm2gMCxrDmjQ0CyNCqhQ4Co9b+0AMCvJDaiwwC3NHa7QMCv9Hi3wMC/dLu3AMC3NHm2gMCjtCyhw4CpbHqgA0CyNCugA4C/dLm2gMC3NHq0QMCjtCigw4C/dLi3wMCjtC+hA4CqvCJ9QoC3NHu3AMC3NHi3wMC6dGenA4C3NHy0wMCjtC6mQ4CjtCugA4C3NH+0AMCntDa7QMC/dL61QMCw5bP/gICv9He6AMC8pHaiwwCr9Gyhw4CyNC+hA4CyNCenA4C3NH23gMCr9GqhQ4C3NHe6AMCo9bm2gMCjtC2gg4C+euUqg4C2tqumwgC0sXgkQ8CuLeX+QECj8jxgApe9jsE0eHIDccv+4M6abkehMgNGiFvfFAywO+MpnR0Fw==',
                'rblUserType':type,'StuNum':self.id,'TeaNum':'','Password':self.password,'login': '登录'}
        try:
            response = requests.post(self.login_url,headers=headers,data=data)
        except ConnectionError:
            flash(u'连接教务在线失败！！！')
            return None
        if response.status_code == 404:
            return None
        self.cookies = response.cookies
        return self.cookies


    def get_name(self):
        response = requests.post(self.login_url,cookies=self.cookies)
        selector = etree.HTML(response.text)
        name = selector.xpath('//*[@id="lblMsg"]/font/text()')
        if name:
            return name[0][4:].strip()
        return False





