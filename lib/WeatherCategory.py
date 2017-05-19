import string

class WeatherCategory(object):
    def __init__(self, name, phrases=[]):
        self.name = name
        self.phrases = set()
        for p in phrases:
            self.addPhrase(p)
    
    def addPhrase(self, phrase):
        cleanPhrase = phrase.lstrip("[Light/Heavy] ")
        self.phrases.add(cleanPhrase)
        
    def containsPhrase(self, phrase):
        cleanPhrase = phrase.lstrip("Light ")
        cleanPhrase = cleanPhrase.lstrip("Heavy ")
        return cleanPhrase in self.phrases