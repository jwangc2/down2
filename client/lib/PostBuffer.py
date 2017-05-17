import datetime
from lib.EntryBuffer import EntryBuffer
from tornado.concurrent import Future

class PostBuffer(EntryBuffer):            
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
            
    def __init__(self):
        super().__init__()
        self.id = 0
        
    def entrySortKeyFn(self, entry):
        return PostBuffer.postDateKey
        
    def entryIDfn(self, entry):
        return entry["ID"]
            
    def addLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] + 1)
    
    def removeLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] - 1)
    
    def changeLike(self, postID, likes):
        post = dict(self.cache[postID])
        post["Likes"] = likes
        self.publish([post])
        
    def buildPost(self, msg, weather, temp):
        newPost = {"ID": self.id, "Message": msg, "Weather": weather, "Temperature": temp, "Time": PostBuffer.getISODate(), "Likes": 0}
        self.id += 1
        return newPost