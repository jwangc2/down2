import os
import sys
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from lib.PostBuffer import PostBuffer
from lib.PostHandler import PostHandler
from lib.LikeHandler import LikeHandler
from lib.UserHandler import UserHandler

if __name__ == '__main__':
    # Setup the data
    data = {}
    globalPostBuffer = PostBuffer(data=data)
    httpClient = AsyncHTTPClient()
    globalArgs = {
        "postBuffer": globalPostBuffer,
        "httpClient": httpClient,
        "userActivity": {}
    }
    
    # Settings
    root = os.path.dirname(__file__)
    port = 8888
    useMockup = False

    settings = {
        "static_path": root,
        "cookie_secret": "a6301483f77f60",
        "xsrf_cookies": True,
    }
    
    # Build application
    application = tornado.web.Application([
        (r"/api/checkin", UserHandler, globalArgs),
        (r"/api/posts/submit", PostHandler, globalArgs),
        (r"/api/posts/like", LikeHandler, globalArgs),
        (r"/api/posts", PostHandler, globalArgs),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "public/index.html"}),
    ])
    
    # Run
    try:
        for arg in sys.argv[1:]:
            if arg == "-m":
                useMockup = True
                print("Using mockup...")
        globalPostBuffer.newMessages([globalPostBuffer.buildPost("[System] Welcome!", "Any", 69)])
        application.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
        httpClient.close()