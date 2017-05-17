from lib.JsonHandler import JsonHandler
import tornado.web
from tornado.concurrent import Future
from tornado import gen
from Lib import uuid

class UserHandler(JsonHandler):
    apikey = "9ad1eeb07ab80737"
    baseUrl = "http://api.wunderground.com/api/" + apikey
    
    def initialize(self, postBuffer, httpClient, userActivity, weatherCategories):
        self.userActivity = userActivity
        self.httpClient = httpClient
        self.weatherCategories = weatherCategories
    
    @gen.coroutine
    def get(self):
        userFuture = Future()
        
        # determine guid
        guid = None
        while guid is None or str(guid) in self.userActivity.keys():
            guid = uuid.uuid4()
            
        # get and set user data
        ip = self.request.remote_ip
        self.getLocation(ip, lambda response: self.getConditions(response.body, lambda lat, lon, response2: self.setUserFuture(userFuture, str(guid), lat, lon, response2.body)))
        userEntry = yield userFuture
        userID = userEntry["UserID"]
        self.userActivity[userID] = userEntry
        self.response = {"UserID": userID}
        self.write_json()
        
    def getLocation(self, ip, handler):
        if ip is None:
            query = "https://ipinfo.io/json"
        else:
            query = "https://ipinfo.io/%s/json"%ip
        self.httpClient.fetch(query, lambda response : self.locationHandler(response, handler))
        
    def locationHandler(self, response, handler):
        json_ipinfo = tornado.escape.json_decode(response.body)
        if "bogon" in json_ipinfo and json_ipinfo["bogon"]:
            self.getLocation(None, handler)
        else:
            handler(response)
    
    def getConditions(self, ipinfo, handler):
        json_ipinfo = tornado.escape.json_decode(ipinfo)
        locSplit = json_ipinfo["loc"].split(",")
        lat = float(locSplit[0])
        lon = float(locSplit[1])
        
        query = "%s/%s/q/%s,%s.json"%(UserHandler.baseUrl, "conditions", lat, lon)
        self.httpClient.fetch(query, lambda response: handler(lat, lon, response))
    
    def setUserFuture(self, userFuture, userID, lat, lon, fullConditions):
        json_fullConditions = tornado.escape.json_decode(fullConditions)
        current_observation = json_fullConditions["current_observation"]
        temp = int(current_observation["temp_f"])
        weather = current_observation["weather"]
        category = self.getWeatherCategory(weather)
        userFuture.set_result({"UserID": userID, "Loc": {"Lat": lat, "Lon": lon}, "Conditions": {"Weather": category.name, "Temperature": temp}, "Liked": set()})
        
    def getWeatherCategory(self, phrase):
        for category in self.weatherCategories:
            if category.containsPhrase(phrase):
                return category
        return self.weatherCategories[-1]