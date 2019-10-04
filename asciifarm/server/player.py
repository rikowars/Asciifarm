
# this package is not used, but it is important that it is imported before any component modules
# importing components before gameobjects is loaded will result in a cyclic dependency problem
from . import gameobjects


from .components import Select
from .datacomponents import Inventory, Attackable, Move, Fighter, Heal, Input, Faction, Listen, Equipment
from .template import Template
from . import entity

class Player:
    
    def __init__(self, name, world):
        
        self.name = name
        self.world = world
        self.roomname = None
        self.entity = None
        self.inventory = Inventory(10)
        self.equipment = Equipment({"hand": None, "body": None})
        self.health = None
        self.maxHealth = 50
        self.messages = [] # actually a queue
        self.resetView = True
        self.changes = set()
        self.canChangeRoom=False
        
    
    def getName(self):
        return self.name
    
    def leaveRoom(self):
        if self.entity:
            self.health = self.getHealthPair()[0]
            self.entity.remove()
            self.entity = None
    
    def joinRoom(self, roomname, place=None):
        self.canChangeRoom = False
        room = self.world.getRoom(roomname)
        if not room:
            room = self.world.getDefaultRoom()
        roomname = room.getName()
        
        if self.entity:
            self.leaveRoom()
        
        pos = place or room.getEntrance()
        self.entity = entity.Entity(
            sprite = "player",
            height = 2,
            name = '&' + self.name,
            components={
                #"equipment": self.equipment,
                "select": Select()
            }, dataComponents=[
                self.inventory,
                self.equipment,
                Faction.GOOD,
                Input(),
                Listen(),
                Move(slowness=2),
                Heal(interval=50),
                Fighter(strength=5, slowness=8),
                Attackable(maxHealth=self.maxHealth, health=self.health or self.maxHealth)
            ]
        )
        roomData = room.getRoomData()
        self.entity.construct(roomData)
        for item in self.inventory.items:
            item.construct(roomData)
        for item in self.equipment.slots.values():
            item.construct(roomData)
        for attr in dir(self):
            if attr.startswith("on_"):
                self.entity.addListener(attr[3:], self.__getattribute__(attr))
        room.addObj(pos, self.entity)
        self.roomname = roomname
        self.place = pos
        self.resetView = True
        self.canChangeRoom = True
    
    def getRoom(self):
        return self.roomname
    
    
    def on_changeroom(self, o, room, pos):
        room = room.format(player=self.name, name=o.getName())
        if self.canChangeRoom:
            self.joinRoom(room, pos)
    
    def on_attack(self, o, obj, damage):
        self.log("{} attacks {} for {} damage".format(self.name, obj.getName(), damage), "attack")
    
    def on_kill(self, o, obj):
        self.log("{} kills {}".format(self.name, obj.getName()), "kill")
    
    def on_damage(self, o, obj, damage):
        self.log("{} got {} damage from {}".format(self.name, damage, obj.getName()), "damage")
        self.changes.add("health")
    
    def on_heal(self, o, obj, health):
        if obj:
            self.log("{} got {} health from {}".format(self.name, health, obj.getName()), "heal")
        self.changes.add("health")
    
    def on_die(self, o, obj):
        self.log("{} got killed by {}".format(self.name, obj.getName()))
        self.entity = None
        self.roomname = None
        self.place = None
        self.health = self.maxHealth
    
    def on_inventorychange(self, o):
        self.changes.add("inventory")
        
    def on_equipmentchange(self, o):
        self.changes.add("equipment")
    
    def on_objectenter(self, o, obj):
        self.changes.add("ground")
    
    def on_objectleave(self, o, obj):
        self.changes.add("ground")
    
    def on_move(self, o):
        self.changes.add("ground")
        self.changes.add("pos")
    
    def on_selection(self, o, obj):
        self.changes.add("selection")
    
    def control(self, action):
        if not self.entity or not (isinstance(action, list) or isinstance(action, tuple)) or len(action) < 1:
            return
        self.entity.getDataComponent(Input).action = action
    
    def getHealthPair(self):
        if self.entity:
            return self.entity.getDataComponent(Attackable).getHealth()
        else:
            return (0, None)
    
    def getHealth(self):
        h = self.getHealthPair()
        if h:
            return h[0]
        if not self.isActive():
            return self.health
        return None
    
    def getInventory(self):
        if self.entity:
            return self.inventory.items
        else:
            return []
    
    def getEquipment(self):
        if self.entity:
            return self.equipment.slots
        else:
            return {}
    
    def getInteractions(self):
        return NotImplemented
        #if not self.entity:
            #return []
        #controller = self.entity.getComponent("controller")
        #return controller.getInteractions()
    
    def getGroundObjs(self):
        if not self.entity:
            return []
        objs = list(self.entity.getGround().getObjs())
        if self.entity in objs:
            objs.remove(self.entity)
        return objs
    
    def getPos(self):
        if not self.entity:
            return None
        return self.entity.getGround().getPos()
    
    def getSelected(self):
        if not self.entity:
            return None
        return self.entity.getComponent("select").getSelected()
    
    def shouldResetView(self):
        return self.resetView
    
    def viewResetDone(self):
        self.resetView = False
    
    def log(self, msg, typ="world"):
        self.messages.append([msg, typ])
        print(msg)
    
    def readMessages(self):
        messages = []
        listen = self.entity.getDataComponent(Listen)
        for source, text in listen.sounds:
            if source is not None:
                text = source.getName() + ": " + text
            messages.append([text, "world"])
        listen.sounds = []
        return messages
    
    def readChanges(self):
        changes = self.changes
        self.changes = set()
        return changes
    
    def isActive(self):
        return bool(self.roomname and self.entity)
    
    def toJSON(self):
        return {
            "name": self.name,
            "roomname": self.roomname,
            "inventory": {"capacity": self.inventory.capacity, "items": [item.serialize().toJSON() for item in self.inventory.items]},
            "equipment": {slot: item.serialialize().toJSON() for slot, item in self.equipment.slots.items()},
                #self.equipment.toJSON(),
            "health": self.getHealth(),
            "maxhealth": self.maxHealth
        }
    
    @classmethod
    def fromJSON(cls, data, world):
        self = cls(data["name"], world)
        self.health = data["health"]
        self.maxHealth = data["maxhealth"]
        self.inventory = Inventory(data["inventory"]["capacity"], [gameobjects.createEntity(Template.fromJSON(item)) for item in data["inventory"]["items"]])
        self.equipment =  Equipment({slot: gameobjects.createEntity(Template.fromJSON(item)) for slot, item in data["equipment"].items() if item is not None})
        #Equipment.fromJSON(data["equipment"])
        self.roomname = data["roomname"]
        
        return self
