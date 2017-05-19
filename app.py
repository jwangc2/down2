import os
import sys
import csv
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from lib.PostBuffer import PostBuffer
from lib.EmergencyBuffer import EmergencyBuffer
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
    
def getEmergencyData(mHttpClient, url, emergencyBuffer):
    print("Fetching emergency data...")
    mHttpClient.fetch(url, lambda response : handleEmergencyResponse(response, emergencyBuffer))
    
def handleEmergencyResponse(response, emergencyBuffer):
    # Parse
    emergencies = []
    responseJson = tornado.escape.json_decode(response.body)
    entry = responseJson["feed"]["entry"]
    for row in entry:
        csvRow = row["content"]["$t"]
        rowDict = parseDict(csvRow)
        emergency = emergencyBuffer.buildEmergency(
            float(rowDict["lat"]),
            float(rowDict["lon"]),
            float(rowDict["radius"]),
            rowDict["source"],
            rowDict["message"]
        )
        emergencies.append(emergency)
        
    # publish to the EmergencyBuffer
    if len(emergencies) > 0:
        emergencyBuffer.publish(emergencies, overwrite=True)
    
def parseDict(dictStr, delim=","):
    outDict = {}
    strArr = dictStr.split(delim)
    for entryStr in strArr:
        kvp = entryStr.split(":")
        key = kvp[0].strip(" ")
        val = kvp[1].strip(" ")
        outDict[key] = val
    return outDict
    
    
if __name__ == '__main__':
    # Setup the data
    data = {}
    globalPostBuffer = PostBuffer()
    globalEmergencyBuffer = EmergencyBuffer()
    httpClient = AsyncHTTPClient()
    globalArgs = {
        "postBuffer": globalPostBuffer,
        "emergencyBuffer": globalEmergencyBuffer,
        "httpClient": httpClient,
        "userActivity": {},
        "weatherCategories": buildWeatherCategories("./weather_categories.csv")
    }
    emergencyUrl = "https://spreadsheets.google.com/feeds/list/1GceRIgyoGZTKfC7mx1Pl4D0GoNGJugTMSajYfdtZOmE/od6/public/basic?alt=json"
    
    # Settings
    root = os.path.dirname(__file__)
    port = int(os.environ.get('DOWN2_SERVICE_PORT', '8888'))
    ip = '0.0.0.0'
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
    emergencyCallback = lambda : getEmergencyData(httpClient, emergencyUrl, globalEmergencyBuffer)
    emergencyPoller = tornado.ioloop.PeriodicCallback(emergencyCallback, 5 * 60000)
    
    # Run
    try:
        emergencyCallback()
        emergencyPoller.start()
        globalPostBuffer.publish([globalPostBuffer.buildPost("[System] Welcome!", "Sunny", 79)])
        application.listen(port, ip)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
        emergencyPoller.stop()
        httpClient.close()