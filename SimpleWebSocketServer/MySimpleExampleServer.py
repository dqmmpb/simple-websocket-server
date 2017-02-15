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
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
from optparse import OptionParser

clients = []

# 设置编码格式
reload(sys)
sys.setdefaultencoding('utf8')

# 线程共享条件
condition = threading.Condition()
# 消息队列，最多存放10条消息
products = Queue.Queue(maxsize=10)

# 广播当前消息
def broadcastMessage(message):
   for client in clients:
      if client.unicom:
         client.sendMessage(u'' + message)

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
            if not products.full():
               message = "新消息，发送时间" + time.strftime('%Y-%m-%d %H:%M:%S')
               products.put("message: " + message)
               print ("{}：产生1条新消息：{}".format(self.getName(), message))
               condition.notify()
            else:
               #print ("消息队列已满，暂时不产生新消息")
               condition.wait()
            condition.release()
            time.sleep(2)

# 消耗消息，讲消息从消息队列中去除，当消息队列为空时，暂停取出，每2秒检测下消息队列
class Consumer(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      self.setName("消费者")
   def run(self):
      global condition, products

      while True:
         if condition.acquire():
            if not products.empty():
               # 当消息队列不空时，取出一条消息，广播该消息
               message = products.get()
               broadcastMessage(message)
               print ("{}：读取并发送1条消息：{}".format(self.getName(), message))
               condition.notify()
            else:
               print ("消息队列为空，暂停读取消息")
               condition.wait()
            condition.release()
            time.sleep(2)


class SimpleSend(WebSocket):

   def __init__(self, server, sock, address):
      WebSocket.__init__(self, server, sock, address)
      # 联通解析开关 True:开启 False:关闭
      self.unicom = False

   def handleMessage(self):
      # 解析发送过来的控制参数，JSON格式
      reqData = json.loads(self.data)
      if(reqData['type'] == 'unicom'):
         if reqData['status']:
            self.unicom = True
            self.sendMessage(u'开启联通解析')
         else:
            self.unicom = False
            self.sendMessage(u'关闭联通解析')

   def handleConnected(self):
      print (self.address, 'connected')
      clients.append(self)

   def handleClose(self):
      clients.remove(self)
      print (self.address, 'closed')


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   (options, args) = parser.parse_args()

   server = SimpleWebSocketServer(options.host, options.port, SimpleSend)

   # 生产者，消费者线程
   p = Producer()
   p.setDaemon(True)
   p.start()
   c = Consumer()
   c.setDaemon(True)
   c.start()

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
