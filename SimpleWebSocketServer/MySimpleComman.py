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
# 消息队列，最多存放10条消息
products = Queue.Queue(maxsize=10)

# 退出
is_exit = False


# 广播当前消息
def broadcastMessage(message):
    print "  消息内容: " + message


# 产生消息，将消息放入消息队列中，当消息队列已满后，暂停产生，每2秒检测以下消息队列
class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("生产者")

    def run(self):
        self.doProduct()

    def doProduct(self):
        global condition, products

        while True:
            if condition.acquire():
                if is_exit:
                    condition.notifyAll()
                    condition.relase()
                    break
                if not products.full():
                    message = time.strftime('%Y-%m-%d %H:%M:%S')
                    products.put(message)
                    print ("{}：产生1条新消息，消息总数：{}".format(self.getName(), products.qsize()))
                    condition.notify()
                else:
                    # print ("消息队列已满，暂时不产生新消息")
                    condition.wait()
                condition.release()
                time.sleep(2)


# 消耗消息，讲消息从消息队列中去除，当消息队列为空时，暂停取出，每2秒检测下消息队列
class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("消费者")

    def run(self):
        self.doSend()

    def doSend(self):
        global condition, products

        while True:
            if condition.acquire():
                if is_exit:
                    condition.notifyAll()
                    condition.relase()
                    break
                if not products.empty():
                    # 当消息队列不空时，取出一条消息，广播该消息
                    message = products.get()
                    print ("{}：读取1条消息，消息总数：{}".format(self.getName(), products.qsize()))
                    broadcastMessage(message)
                    condition.notify()
                else:
                    print ("消息队列为空，暂停读取消息")
                    condition.wait()
                condition.release()
                time.sleep(2)


if __name__ == "__main__":

    # 生产者，消费者线程
    p = Producer()
    p.setDaemon(True)
    p.start()
    c = Consumer()
    c.setDaemon(True)
    c.start()


    def close_sig_handler(signal, frame):
        global is_exit
        is_exit = True
        sys.exit()


    signal.signal(signal.SIGINT, close_sig_handler)

    while True:
        alive = False
        alive = alive or p.isAlive() or c.isAlive()
        if not alive:
            break
