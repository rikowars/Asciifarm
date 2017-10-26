
import curses



class HealthPad:
    
    
    
    def __init__(self, width=1):
        self.pad = curses.newpad(2, width+1)
        self.width = width
        self.changed = False
        self.lastView = None
    
    def setHealth(self, health, maxHealth):
        self.pad.erase()
        self.pad.addstr(0,0,"Health: {}/{}".format(health, maxHealth)[:self.width])
        self.pad.addstr(1,0, ("@"*round(health/maxHealth * self.width)+"-"*self.width)[:self.width])
        self.changed = True
    
    def getHeight(self):
        return 2
    
    def update(self, screen, x, y, xmax, ymax):
        if not self.changed and (x, y, xmax, ymax) == self.lastView:
            return
        self.lastView = (x, y, xmax, ymax)
        self.changed = False
        self.pad.noutrefresh(
            0,
            0,
            y,
            x,
            ymax-1,
            xmax-1)