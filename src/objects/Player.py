
from src.objects.Color import Color

from src.functions import *
from src.Stats import Stats

from src.objects.NetObj import NetObj

from src.objects.Team import Team

class Player(NetObj):
	def __init__(this, _id=0, name=""):
		this.id = int(_id);
		this.ownerid = 0;
		this.name = name;
		this.gid = "";
		this.color = Color();
		
		this.chatting, this.spectating = False, True;
		
		this.isAI = False;
		
		this.score = 0;
		this.ping = 0;
		
		this.pingCharity = 100;
		
		this.stats = Stats();
		
		this.cycleID = 0;
		this.teamID, this.nextTeamID = 0, 0;
	
	def getStats(this):
		stats = Stats.byPlayer.get(this.logName());
		if( stats ):
			this.stats = stats;
	
	def addStats(this):
		if( this.name ):
			Stats.byPlayer[this.logName()] = this.stats;
	
	def onDestroy(this):
		this.addStats();
		engine.players.remove(this);
	
	def __del__(this):
		pass;
	
	def logName(this):
		if( this.gid ):
			return this.gid;
		else:
			return filterStr(removeColors(this.name));
	
	@property
	def team(this):
		if( this.teamID ):
			t = NetObj.objs.get(this.teamID);
			if( isinstance(t, Team) ):
				return t;
		return None;
	
	def readNet(this, msg):
		this.addStats(); # save stats first
		
		this.color.readNet(msg);
		
		this.pingCharity = msg.getShort();
		
		this.name = msg.getString();
		
		#print(this.name);
		
		msg.ping = int(round(msg.getFloat()*1000));
		
		flags = msg.getShort();
		this.chatting = bool(flags&1);
		this.spectating = bool(flags&2);
		
		this.score = msg.getInt();
		
		msg.getBool();  # newdisc
		
		this.nextTeamID = msg.getShort();
		this.teamID = msg.getShort();
		this.idealPlayersPerTeam = msg.getShort();
		
		this.getStats(); # get stats last
	
	
	@staticmethod
	def setEngine(e):
		global engine; engine = e;
		return engine;

