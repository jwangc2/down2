import os
import json
import tornado.ioloop
import tornado.web

id = 3
data = {
    "data": [
        {"id": 1, "author": "Pete Hunt", "text": "This is one comment"},
        {"id": 2, "author": "Jordan Walke", "text": "This is *another* comment"}
    ]
}

class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = tornado.escape.json_decode(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)

class DataHandler(JsonHandler):
    def get(self):
        self.response = data
        self.write_json()
        
    def post(self):
        global id, data
        author = self.request.arguments["author"]
        text = self.request.arguments["text"]
        data["data"].append(
            {"id": id, "author": author, "text": text}
        )
        id += 1
        self.response = data
        self.write_json()

root = os.path.dirname(__file__)
port = 8888

settings = {
    "static_path": root,
    "cookie_secret": "a6301483f77f60",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/api/comments", DataHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "public/index.html"}),
])

if __name__ == '__main__':
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()