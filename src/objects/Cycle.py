
from src.objects.Color import Color

from src.functions import *
from src.Stats import Stats

from src.objects.NetObj import NetObj

class Cycle(NetObj):
	def __init__(this, _id=0, owner=0):
		this.id = int(_id);
		this.ownerid = int(owner);
		
		this.player = None;
	
	def readNetInit(this, msg):
		NetObj.readNetInit(this, msg);
		this.player = NetObj.objs.get(this.ownerid);
	
	def readNet(this, msg):
		pass;
	
	def onDestroy(this):
		engine.cycles.remove(this);
	
	
	@staticmethod
	def setEngine(e):
		global engine; engine = e;
		return engine;
