#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)

        # check if self.data is empty
        if self.data == "":
            return
        
        # check if the method is allowed: only GET
        if self.data.split()[0].decode() != "GET":
           
            self.request.sendall(bytearray(self.get_response("405"),'utf-8'))
            return

        new_data = self.data
        
        self.getGET(new_data)

        return
    

    def getGET(self, data):
        """
        Processes the GET command
        Inputs:
            data: the data regarding the request being made
        Outputs:
            None
        """

        # get the direcoty www is in right now
        cwd = os.getcwd()
        cwd_www = os.path.join(cwd, "www")

        file_path_from_request = data.split()[1].decode()

        # attach the path to ...../www/
        if (file_path_from_request[0] == "/"):
            file_path = os.path.join(cwd_www, file_path_from_request[1:])
        else:
            file_path = os.path.join(cwd_www, file_path_from_request)
        abs_file_path = os.path.realpath(file_path) # returns the absolute path: removes the ".././.." stuff

        # check if are in the correct directory (https://www.geeksforgeeks.org/python-os-path-commonprefix-method/)
        if os.path.commonprefix([cwd_www, abs_file_path]) != cwd_www:
            self.request.sendall(bytearray(self.get_response("404"),'utf-8'))
            return
        
        # check if abs_file_path is valid and if there is a trailing /
        if os.path.isdir(abs_file_path) and not file_path_from_request.endswith("/"):
            self.request.sendall(bytearray(self.get_response("301", path=abs_file_path),'utf-8'))
            return

        # if abs_file_path is a directoy, open index.html in it (https://stackoverflow.com/a/15077441/11656468)
        if os.path.exists(abs_file_path) and os.path.isdir(abs_file_path):
            abs_file_path = os.path.join(abs_file_path, "index.html")
           
        # if it neither a file not a directory, return 404
        elif not os.path.exists(abs_file_path):
            self.request.sendall(bytearray(self.get_response("404", abs_file_path),'utf-8'))
            return

        file = open(abs_file_path, "r")
        file_data = file.read()
        
        if abs_file_path.endswith(".css"):
            self.request.sendall(bytearray(self.get_response("200", content_type="css", body=file_data.encode()),'utf-8'))
        else:
            self.request.sendall(bytearray(self.get_response("200", content_type="html", body=file_data.encode()),'utf-8'))


        file.close()
        return
            
    

    def get_status_code_description(self, status_code):
        """
        Returns the description of the Status code
        Inputs:
            status_code: the status code
        Outputs:
            The description of the status code
        """
        status_code_descriptions = {
            "405": "Method Not Allowed",
            "301": "Moved Permanently",
            "404": "Not Found",
            "200": "OK"
        }

        return status_code_descriptions[status_code]
    
    def get_response(self, status_code, content_type=None, path=None, body=None):
        """
        Generates a response for each status_code
        Inputs:
            status_code: the status code
            content_type: html or css
            path: the path of the file
            body: the body of the file to be rendered, if any
        Output:
            The generated response
        """
        if status_code == "405":
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405

            http_response = f"HTTP/1.1 {status_code} {self.get_status_code_description(status_code)}\r\nAllow: GET\r\n\r\nContent-length:0"

            return http_response
        
        elif status_code == "301":
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301

            http_response = f"HTTP/1.1 {status_code} {self.get_status_code_description(status_code)}\r\n Location: {path}/\r\nContent-length:0\r\nConnection: close"
            return http_response

        elif status_code == "404":
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404

            http_response = f"HTTP/1.1 {status_code} {self.get_status_code_description(status_code)}\r\nContent-length:0"

            return http_response
        
        
        elif status_code == "200":
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200
            use_body = body

            if (content_type == None):
                use_body = f"<p>{self.get_status_code_description(status_code)}</p>"

            http_response = f"HTTP/1.1 {status_code} {self.get_status_code_description(status_code)}\r\nContent-length:" + str(len(body)) + f"\r\nContent-Type: text/{content_type}\r\n\r\n" + use_body.decode()

            return http_response

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
