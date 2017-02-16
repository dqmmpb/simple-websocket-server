## A Simple Websocket Server written in Python

- RFC 6455 (All latest browsers)
- TLS/SSL out of the box
- Passes Autobahns Websocket Testsuite
- Support for Python 2 and 3

#### Installation

You can install SimpleWebSocketServer by running the following command...

`sudo pip install git+https://github.com/dpallot/simple-websocket-server.git`

Or by downloading the repository and running `sudo python setup.py install`.  
Installation via pip is suggested.

#### Echo Server Example
`````python
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client
        self.sendMessage(self.data)

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'

server = SimpleWebSocketServer('', 8000, SimpleEcho)
server.serveforever()
`````

Open *websocket.html* and connect to the server.

#### Chat Server Example
`````python
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

clients = []
class SimpleChat(WebSocket):

    def handleMessage(self):
       for client in clients:
          if client != self:
             client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
       print self.address, 'connected'
       for client in clients:
          client.sendMessage(self.address[0] + u' - connected')
       clients.append(self)

    def handleClose(self):
       clients.remove(self)
       print self.address, 'closed'
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')

server = SimpleWebSocketServer('', 8000, SimpleChat)
server.serveforever()
`````
Open multiple *websocket.html* and connect to the server.

#### Want to get up and running faster?

There is an example which provides a simple echo and chat server

Echo Server

    python SimpleExampleServer.py --example echo

Chat Server (open up multiple *websocket.html* files)

    python SimpleExampleServer.py --example chat


#### TLS/SSL Example

1) Generate a certificate with key

    openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem

2) Run the secure TSL/SSL server (in this case the cert.pem file is in the same directory)

    python SimpleExampleServer.py --example chat --ssl 1 --cert ./cert.pem

3) Offer the certificate to the browser by serving *websocket.html* through https.
The HTTPS server will look for cert.pem in the local directory.
Ensure the *websocket.html* is also in the same directory to where the server is run.

    sudo python SimpleHTTPSServer.py

4) Open a web browser to: *https://localhost:443/websocket.html*

5) Change *ws://localhost:8000/* to *wss://localhost:8000* and click connect.

Note: if you are having problems connecting, ensure that the certificate is added in your browser against the exception *https://localhost:8000* or whatever host:port pair you want to connect to.

#### For the Programmers

handleConnected: called when handshake is complete
 - self.address: TCP address port tuple of the endpoint

handleClose: called when the endpoint is closed or there is an error

handleMessage: gets called when there is an incoming message from the client endpoint
 - self.opcode: the WebSocket frame type (STREAM, TEXT, BINARY)
 - self.data: bytearray (BINARY frame) or unicode string payload (TEXT frame)  
 - self.request: HTTP details from the WebSocket handshake (refer to BaseHTTPRequestHandler)

sendMessage: send some text or binary data to the client endpoint
 - sending data as a unicode object will send a TEXT frame
 - sending data as a bytearray object will send a BINARY frame

sendClose: send close frame to endpoint


---------------------
The MIT License (MIT)
# 新增的生产者/消费者模式的例子

``` python
 python MySimpleExampleServer.py
```

websocket的默认端口是8000，启动后，用浏览器打开mywebsocket.html页面

 - **开启联通解析** 开启联通解析开关，发送 unicom: true
 - **关闭联通解析** 关闭联通解析开关，发送 unicom: false
 - **清除** 清除textarea中的内容
 - **断开** 断开websocket
 - **连接** 连接websocket

先点“连接”，然后再点“开启联通解析”，即可查看效果

生产者线程负责产生消息放入消息队列，消费者线程负责从消息队列中读取消息，并广播到websocket接口，浏览器通过websocket接收并显示

生产者线程和消费者线程作为后台常驻线程一直存在



# 生产者/消费者模式 使用文件

依赖[python-tail][python-tail]插件实现`tail -f`功能
请参考[python-tail][python-tail]插件的安装

`FileWriter.py`负责写文件  
`MySimpleFileServerWithTail.py`负责使用websocket和浏览器通讯

``` python
        # 使用tail插件完成`tail -f`的功能
        t = tail.Tail('thefile.txt')
        # 注册回调，将消息广播给client客户端
        t.register_callback(broadcastMessage)
        t.follow(s=2)
```

## 使用

启动 server

``` python
 python MySimpleFileServerWithTail.py

```

启动 文件Write

``` python
 python FileWrite.py

```


[python-tail]: https://github.com/kasun/python-tail
