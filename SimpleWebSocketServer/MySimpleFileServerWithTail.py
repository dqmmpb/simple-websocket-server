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
import tail

clients = []

# 设置编码格式
reload(sys)
sys.setdefaultencoding('utf8')

# 线程共享条件
condition = threading.Condition()

# 广播当前消息
def broadcastMessage(message):
    message = message.strip()
    if message:
        message = message.strip()
        print message
        for client in clients:
            if client.unicom:
                client.sendMessage(u'' + message)


# 消耗消息，将消息从文件中取出，每2秒读取1条消息
class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("消费者")

    def run(self):
        self.doSend()

    def doSend(self):
        global condition

        try:
            # 使用tail插件完成`tail -f`的功能
            t = tail.Tail('thefile.txt')
            # 注册回调，将消息广播给client客户端
            t.register_callback(broadcastMessage)
            t.follow(s=2)
        except Exception as TailError:
            print 'error'



class SimpleSend(WebSocket):
    def __init__(self, server, sock, address):
        WebSocket.__init__(self, server, sock, address)
        # 联通解析开关 True:开启 False:关闭
        self.unicom = False

    def handleMessage(self):
        # 解析发送过来的控制参数，JSON格式
        reqData = json.loads(self.data)
        if (reqData['type'] == 'unicom'):
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

    # 消费者线程
    c = Consumer()
    c.setDaemon(True)
    c.start()

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()


    signal.signal(signal.SIGINT, close_sig_handler)

    server.serveforever()
