
from src.objects.Color import Color

from src.functions import *
from src.Stats import Stats

from src.objects.NetObj import NetObj

class Team(NetObj):
	def __init__(this, _id=0, name=""):
		this.id = int(_id);
		this.name = name;
		
		this.color = Color();
		
		this.score = 0;
		
		this.maxPlayers = 0;
		this.maxImbalance = 3;
	
	def onDestroy(this):
		engine.teams.remove(this);
	
	def readNet(this, msg):
		this.color.readNet(msg);
		this.name = msg.getStr();
		this.maxPlayers = msg.getInt();
		this.maxImbalance = msg.getInt();
		this.score = msg.getInt();
	
	
	@staticmethod
	def setEngine(e):
		global engine; engine = e;
		return engine;

