
import playerent

class Player:
    
    def __init__(self, name, world):
        
        self.name = name
        self.world = world
        
        self.roomname = None
        #self.pos = (0,0)
        
        self.entity = None
        
        self.data = {}
        
        self.controller = {}
        
    
    def updateData(self):
        if self.entity:
            pass
    
    def leaveRoom(self):
        self.entity.remove()
    
    def joinRoom(self, roomname, place=None):
        room = self.world.getRoom(roomname)
        if not room:
            raise Exception("Invalid Room")
        
        if self.entity:
            self.leaveRoom()
        
        self.roomname = roomname
        if isinstance(place, list) or isinstance(place, tuple):
            pos = place
        elif isinstance(place, str):
            pos = room.getPlace(place)
        else:
            pos = room.getEntrance()
        self.entity = playerent.Player(room, pos)
        self.entity.setController(self.controller)
        self.entity.getEvent().addListener(self.onPlayerAction)
        room.addObj(pos, self.entity)
    
    def getRoom(self):
        return self.roomname
    
    def getPos(self):
        if self.entity:
            return self.entity.getPos()
        else:
            return None
    
    def onPlayerAction(self, action, *data):
        if action == "changeroom":
            room, pos = data
            self.joinRoom(room, pos)
    
    def getInventory(self):
        if self.entity:
            return self.entity.holding
        else:
            return None
    
    def control(self, action):
        self.controller["action"] = action
            
    
