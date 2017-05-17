import os
import sys
import csv
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from lib.PostBuffer import PostBuffer
from lib.PostHandler import PostHandler
from lib.LikeHandler import LikeHandler
from lib.UserHandler import UserHandler
from lib.EmergencyHandler import EmergencyHandler
from lib.WeatherCategory import WeatherCategory

def buildWeatherCategories(fname):
    categories = []
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        isFirst = True
        rowGen = None
        for row in reader:
            if rowGen is None:
                rowGen = range(len(row))
            for i in rowGen:
                if isFirst:
                    categories.append(WeatherCategory(row[i]))
                else:
                    if len(row[i]) > 0:
                        categories[i].addPhrase(row[i])
            isFirst = False
            
    return categories
if __name__ == '__main__':
    # Setup the data
    data = {}
    globalPostBuffer = PostBuffer()
    httpClient = AsyncHTTPClient()
    globalArgs = {
        "postBuffer": globalPostBuffer,
        "httpClient": httpClient,
        "userActivity": {},
        "weatherCategories": buildWeatherCategories("./weather_categories.csv")
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
        (r"/api/emergency", EmergencyHandler, globalArgs),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "public/index.html"}),
    ])
    
    # Run
    try:
        globalPostBuffer.publish([globalPostBuffer.buildPost("[System] Welcome!", "Sunny", 79)])
        application.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
        httpClient.close()