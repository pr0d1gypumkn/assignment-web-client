#  Copyright 2023 Ahmed Keshta

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse as parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        response = b''
        body = False
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
            if b'\r\n\r\n' in response and body:
                break
            elif b'\r\n\r\n' in response:
                body = True
        return response.decode()

    def GET(self, url, args=None):
        code = 500
        body = ''
        url = parse.urlparse(url)
        path = url.path
        if not path:
            path = "/"
        elif not path.endswith("/") and not path.endswith(".html") and not path.endswith(".css"):
            path += "/"
        
        
        host = url.hostname
        port = url.port
        if not port:
            port = 80

        self.connect(host, port)
        request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n"
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)
        
        self.close()
        status = 0

        status = int(response.split("\r\n")[0].split(" ")[1])
        response = response.split("\r\n\r\n")
        if len(response) > 1:
            body = response[1]
        code = int(status)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ''
        if args:
            vars = parse.urlencode(args)
        else:
            vars = parse.urlencode({})
        url = parse.urlparse(url)
        path = url.path
        if not path.endswith("/"):
            path += "/"
        
        port = url.port
        if not port:
            port = 80
        host = url.hostname
        request = f"POST {path} HTTP/1.1\r\n" + \
                   f"Host: {host}\r\n" + \
                   "Content-Type: application/x-www-form-urlencoded\r\n" + \
                   "Connection: close\r\n" + \
                   f"Content-Length: {len(vars)}\r\n\r\n{vars}\r\n"
        
        self.connect(host, port)
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)
        self.close()
        response = response.split("\r\n\r\n")
        if len(response) > 1:
            body = response[1]
        code = int(response[0].split(" ")[1])
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
