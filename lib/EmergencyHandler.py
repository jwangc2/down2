from lib.JsonHandler import JsonHandler
from lib.PostBuffer import PostBuffer
import tornado.web
from tornado.concurrent import Future
from tornado import gen
import time
import math

class EmergencyHandler(JsonHandler):
    
    def initialize(self, postBuffer, emergencyBuffer, httpClient, userActivity, weatherCategories):
        self.postBuffer = postBuffer
        self.emergencyBuffer = emergencyBuffer
        self.userActivity = userActivity
        self.subscriber = None
        
    @gen.coroutine
    def get(self):           
        userID = self.get_argument("UserID", None, True)
        if userID is None or userID not in self.userActivity.keys():
            self.write_error_custom(401, message="Unauthorized request")
        else:
            count = int(self.get_argument("count", 0, True))
            # Yield for new messages
            self.subscriber = self.emergencyBuffer.subscribe(lambda post : EmergencyHandler.emergencyRelevantFn(post, userID), count=count)
            emergencies = yield self.emergencyBuffer.getFuture(self.subscriber)
            if self.request.connection.stream.closed():
                return
                
            # Fulfill the long poll
            self.response = {"emergencies": emergencies}
            self.write_json()
        
    def emergencyRelevantFn(emergency, userID):
        userLat = self.userActivity[userID]["Loc"]["Lat"]
        userLon = self.userActivity[userID]["Loc"]["Lon"]
        
        eLat = emergency["Latitude"]
        eLon = emergency["Longitude"]
        eRad = emergency["Radius"]
        
        return ((userLat - eLat) ** 2) + ((userLon - eLon) ** 2) <= eRad ** 2

    def emergencyRelevantFn(emergency, conditions):
        return True
        
    def on_connection_close(self):
        if self.subscriber is not None:
            self.emergencyBuffer.cancelWait(self.subscriber)