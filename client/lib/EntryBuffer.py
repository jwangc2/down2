import datetime
from tornado.concurrent import Future

class EntryBuffer(object):
            
    def __init__(self):
        self.subscribers = set()
        self.cache = {}
        
    def getRelevantEntries(self, entryList, relevantFn):
        relevantEntries = [entry for entry in entryList if relevantFn(entry)]
        return sorted(relevantEntries, key=self.entrySortKeyFn)
            
    def entrySortKeyFn(self, entry):
        raise NotImplementedError("entrySortKeyFn was not implemented")

    def entryIDfn(self, entry):
        raise NotImplementedError("entryIDfn was not implemented")
        
    def subscribe(self, relevantFn, count=0):
        resultFuture = Future()
        subscriber = (resultFuture, relevantFn)
        pushed = False
        if count < 0:
            count = len(self.cache)
        relevantEntries = self.getRelevantEntries([entry for key, entry in self.cache.items()], relevantFn)
        relevantCount = min(len(relevantEntries), count)
        if relevantCount > 0:
            resultFuture.set_result(relevantEntries[-relevantCount:])
            pushed = True
        if not pushed:
            self.subscribers.add(subscriber)
        return subscriber
        
    def getFuture(self, subscriber):
        return subscriber[0]
        
    def cancelWait(self, subscriber):
        subscriber[0].set_result([])
        self.subscribers.discard(subscriber)
        
    def publish(self, entries, overwrite=False):
        for subscriber in set(self.subscribers):
            relevantEntries = self.getRelevantEntries(entries, subscriber[1])
            if len(relevantEntries) > 0:
                subscriber[0].set_result(relevantEntries)
                self.subscribers.discard(subscriber)
        if overwrite:
            self.cache = {}
        for entry in entries:
            self.cache[self.entryIDfn(entry)] = entry