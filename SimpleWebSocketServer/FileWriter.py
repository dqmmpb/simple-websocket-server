#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
The MIT License (MIT)
Copyright (c) 2013 Dave P.
'''


import signal
import sys
import json
import threading
import time
import Queue
from optparse import OptionParser

# 设置编码格式
reload(sys)
sys.setdefaultencoding('utf8')

# 线程共享条件
condition = threading.Condition()

# 退出
is_exit = False

file_object = open('thefile.txt', 'a+')

# 产生消息，将消息放入消息队列中，当消息队列已满后，暂停产生，每2秒检测以下消息队列
class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("生产者")

    def run(self):
        self.doProduct()
    def doProduct(self):
        global condition

        while True:
            if condition.acquire():
                if is_exit:
                    condition.notifyAll()
                    condition.relase()
                    break
                message =  "新消息，发送时间" + time.strftime('%Y-%m-%d %H:%M:%S')
                file_object.writelines([message + '\n'])
                file_object.flush()
                print ("{}：产生1条新消息，消息内容：{}".format(self.getName(), message))
                condition.notify()
                condition.release()
                time.sleep(2)


if __name__ == "__main__":



    # 生产者线程
    p = Producer()
    p.setDaemon(True)
    p.start()


    def close_sig_handler(signal, frame):
        global is_exit, file_object
        is_exit = True

        file_object.close()
        sys.exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    while True:
        alive = False
        alive = alive or p.isAlive()
        if not alive:
            break
