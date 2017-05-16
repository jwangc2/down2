import datetime
from tornado.concurrent import Future

class PostBuffer(object):
    def __init__(self, data={}):
        self.subscribers = set()
        self.cache = data
        self.id = len(data.keys())
        
    def getRelevantPosts(postList, conditions):
        return postList
        
    def waitForMessages(self, conditions, count=0):
        resultFuture = Future()
        subscriber = (conditions, resultFuture)
        if count > 0:
            relevantPosts = PostBuffer.getRelevantPosts([post for key, post in self.cache.items()], conditions)
            relevantCount = min(len(relevantPosts), count)
            if relevantCount > 0:
                resultFuture.set_result(relevantPosts[-relevantCount:])
            return subscriber
        self.subscribers.add(subscriber)
        return subscriber
        
    def cancelWait(self, subscriber):
        subscriber[1].set_result([])
        self.subscribers.remove(subscriber)
        
    def newMessages(self, messages):
        for subscriber in set(self.subscribers):
            relevantPosts = PostBuffer.getRelevantPosts(messages, subscriber[0])
            if len(relevantPosts) > 0:
                subscriber[1].set_result(relevantPosts)
                self.subscribers.discard(subscriber)
        for message in messages:
            self.cache[message["ID"]] = message
            
    def addLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] + 1)
    
    def removeLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] - 1)
    
    def changeLike(self, postID, likes):
        post = dict(self.cache[postID])
        post["Likes"] = likes
        self.newMessages([post])
        
    def buildPost(self, msg, weather, temp):
        newPost = {"ID": self.id, "Message": msg, "Weather": weather, "Temperature": temp, "Time": PostBuffer.getISODate(), "Likes": 0}
        self.id += 1
        return newPost
        
    def getISODate():
        date = datetime.datetime.utcnow().isoformat().split('.')[0]
        return '%sZ'%date