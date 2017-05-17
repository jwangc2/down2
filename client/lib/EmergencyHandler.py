from lib.JsonHandler import JsonHandler
from lib.PostBuffer import PostBuffer
import tornado.web
from tornado.concurrent import Future
from tornado import gen
import time

class EmergencyHandler(JsonHandler):
    
    def initialize(self, postBuffer, httpClient, userActivity, weatherCategories):
        self.postBuffer = postBuffer
        self.userActivity = userActivity
        
    def get(self):
        self.response = {"emergencies": [
            {"ID": 0, "Source": "Washington Post", "Message": "Hi"},
            {"ID": 1, "Source": "Your momma", "Message": "is..."}
        ]}
        time.sleep(5)
        self.write_json()

    '''@gen.coroutine
    def get(self):
        try:
            userID = self.get_argument("UserID", None, True)
            if userID is None or userID not in self.userActivity.keys():
                self.write_error_custom(401, message="Unauthorized request")
            else:
                # Retrieve our subscriber (conditions, future)
                count = int(self.get_argument("count", 0, True))
                conditionsDict = self.userActivity[userID]["Conditions"]
                conditionsPayload = (conditionsDict["Weather"], conditionsDict["Temperature"])
                self.subscriber = self.postBuffer.subscribe(lambda post : PostHandler.postRelevantFn(post, conditionsPayload), count=count)
                
                # Yield for new messages
                messages = yield self.postBuffer.getFuture(self.subscriber)
                if self.request.connection.stream.closed():
                    return
                    
                # Fulfill the long poll
                self.response = {"data": messages}
                self.write_json()
        except Exception as e:
            print("Error: " + str(e))'''
            
    def emergencyRelevantFn(emergency, conditions):
        return True
        
    def on_connection_close(self):
        #self.postBuffer.cancelWait(self.subscriber)
        pass