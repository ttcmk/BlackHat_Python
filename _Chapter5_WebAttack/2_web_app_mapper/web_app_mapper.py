# -*- coding: utf-8 -*-

# 在自己安装的CMS开源系统中得到各种路径
# 用来访问target网站的各路径得到响应，判断是否存在路径

import Queue
import threading
import os
import urllib2

threads = 10

target = "http://www.blackhatpython.com"
directory = "./Downloads/joomla-3.1.1"
filters = [".jpg", ".gif", ".png", ".css"]

os.chdir(directory)

web_paths = Queue.Queue()

# root, dirnames -- [root下的所有子目录列表], filenames -- [root下的非子目录的文件列表]
for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]

        # "abc.png" => ('abc', '.png')
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s%s" % (target, path)

        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
            content = response.read()

            print "[%d] => %s" % (response.code, path)
            response.close()
        except urllib2.HTTPError as error:
            # print "Failed %s" % error.code
            pass


for i in range(threads):
    print "Spawning thread: %d" % i
    t = threading.Thread(target=test_remote)
    t.start()
