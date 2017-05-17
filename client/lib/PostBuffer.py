import datetime
from tornado.concurrent import Future

class PostBuffer(object):
    timeRangeSeconds = 2 * 3600
    temperatureRange = 5
        
    def getRelevantPosts(postList, conditions):
        relevantPosts = [post for post in postList if PostBuffer.postIsRelevant(post, conditions)]
        return sorted(relevantPosts, key=PostBuffer.postDateKey)
        
    def postIsRelevant(post, conditions):
        timeDiffSeconds = PostBuffer.getDateDiffSeconds(PostBuffer.getISODate(), post["Time"])
        temperatureDiff = post["Temperature"] - conditions[1]
        return (post["Weather"] == conditions[0]
            and timeDiffSeconds >= 0
            and timeDiffSeconds <= PostBuffer.timeRangeSeconds
            and abs(temperatureDiff) <= PostBuffer.temperatureRange)
            
    def getISODate():
        date = datetime.datetime.utcnow().isoformat().split('.')[0]
        return '%sZ'%date
        
    def getDateDiffSeconds(dateStrA, dateStrB):
        dateA = PostBuffer.parseISODate(dateStrA)
        dateB = PostBuffer.parseISODate(dateStrB)
        return (dateA - dateB).total_seconds() 
        
    def parseISODate(dateStr):
        return datetime.datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%SZ")
        
    def postDateKey(post):
        cleanTime = post["Time"].split("T")[1][:-2]
        return tuple(cleanTime.split(":"))
            
    def __init__(self, data={}):
        self.subscribers = set()
        self.cache = data
        self.id = len(data.keys())
        
    def waitForMessages(self, conditions, count=0):
        resultFuture = Future()
        subscriber = (conditions, resultFuture)
        pushed = False
        if count > 0:
            relevantPosts = PostBuffer.getRelevantPosts([post for key, post in self.cache.items()], conditions)
            relevantCount = min(len(relevantPosts), count)
            if relevantCount > 0:
                resultFuture.set_result(relevantPosts[-relevantCount:])
                pushed = True
        if not pushed:
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