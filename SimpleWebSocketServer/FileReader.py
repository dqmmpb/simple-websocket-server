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

file_object = open('thefile.txt', 'r')

# 消耗消息，讲消息从消息队列中去除，当消息队列为空时，暂停取出，每2秒检测下消息队列
class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("消费者")

    def run(self):
        self.doSend()

    def doSend(self):
        global condition

        while True:
            if condition.acquire():
                if is_exit:
                    condition.notifyAll()
                    condition.relase()
                    break
                message = file_object.readline()
                if message:
                    message = message.strip()
                    print ("{}：读取1条消息，消息内容：{}".format(self.getName(), message))
                condition.notify()
                condition.release()
                time.sleep(2)


if __name__ == "__main__":



    # 消费者线程
    c = Consumer()
    c.setDaemon(True)
    c.start()


    def close_sig_handler(signal, frame):
        global is_exit, file_object
        is_exit = True

        file_object.close()
        sys.exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    while True:
        alive = False
        alive = alive or c.isAlive()
        if not alive:
            break
