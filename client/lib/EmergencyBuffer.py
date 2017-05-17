from lib.EntryBuffer import EntryBuffer

class EmergencyBuffer(EntryBuffer):
    def __init__(self):
        super().__init__()
        self.id = 0

    def entrySortKeyFn(self, entry):
        return self.entryIDfn(entry)

    def entryIDfn(self, entry):
        return entry["ID"]
        
    def buildEmergency(self, lat, lon, radius, src, msg):
        e = {
            "ID": self.id,
            "Latitude": lat,
            "Longitude": lon,
            "Radius": radius,
            "Source": src,
            "Message": msg
        }
        self.id += 1
        return e