
import ctypes

from src.functions import *

from src.nMessage import *
from src.objects.netObjects import *

#from src.Stats import Stats


def aarecSetEngine(e): global engine; engine = e;
def aarecSetStats(s): global stats; stats = s;

class AARECState:
	# static variables
	time = 0.0; 
	
	# member variables
	roundWinner = None;
	matchWinner = None; 
	
	consoleMessage = None;#"";
	centerMessage = None;#"";
	chatMessage = None;#"";
	
	obj = None;
	objIsSync = False;
	objIsNew = False;
	objIsDel = False;
	
	@property
	def player(this):
		if(isinstance(this.obj, Player)):
			return this.obj;
		return None;
	
	@property
	def team(this):
		if(isinstance(this.obj, Team)):
			return this.obj;
		return None;
	
	@property
	def cycle(this):
		if(isinstance(this.obj, Cycle)):
			return this.obj;
		return None;
	
	@property
	def zone(this):
		return None;


def parseAAREC(f, encoding="latin1"):
	rline = "\n";
	while( rline ):
		rline = f.readline().decode(encoding);
		
		line = rline.rstrip();
		split = line.split(" ");
		
		if(split[0] == "T"):
			AARECState.time = int(split[1])+(int(split[2])/1e6);
		elif(split[0] == "READ"):
			if(split[1] != "-1"):
				for state in message_read(f.readline().decode(encoding)):
					yield state;
				#f.readline(); # eat next line
		
		yield AARECState();


def seekGetLastAARECTime(f, encoding="latin1"):
	s = AARECState();
	while(True):
		line = f.readline().decode(encoding)
		if( not line ):
			break;
		split = line.split(" ");
		if(split[0] == "T"):
			s.time = int(split[1])+(int(split[2])/1e6);
	return s;


MSG_HAS_LOGGED_IN = r"(.+) has been logged in as (.+) at access level \"(.+)\".";
CEN_ROUND_WINNER = r"Winner: (.+)"
CEN_MATCH_WINNER = r"Match Winner: (.+)"
MSG_CORE_DUMPED = r"(.+) core dumped (.+) for (\d+) points.";
#MSG_RENAMED = r"(+.) renamed to (+.)";

def message_read(msg):
	nums = msg.split();
	for i, n in enumerate(nums):
		nums[i] = ctypes.c_uint8(int(n)).value;
	
	start = 0;
	_len = ((nums[4]<<8)|nums[5])*2;
	while(True):
		#print(start, _len, file=sys.stderr);
		yield message_parse(nums[start:]);
		start += _len+6;
		if( (len(nums)-start) >= (_len+6) ):
			_len = ((nums[start+4]<<8)|nums[start+5])*2;
		else:
			break;

gotIDs = False;

def message_parse(nums):
	msg = nMessage(nums);
	msg.getHeader();
	#print(msg.descriptor, msg.id, msg.len, file=sys.stderr);
	
	state = AARECState();
	
	if( msg.descriptor == 203 ): # chat message
		playerID = msg.getShort();
		p = NetObj.objs.get(playerID);
		chat_raw = msg.getStr();
		if( p and isinstance(p, Player) ):
			chat = removeColors(chat_raw);
			state.obj = p;
			state.chatMessage = chat;
			state.chatMessageRaw = chat_raw;
	
	if( msg.descriptor == 8 ): # console message
		for con_raw in msg.getStr().split("\n"):
			con = removeColors(con_raw);
			state.consoleMessage = con;
			state.consoleMessageRaw = con_raw;
			if(not con): continue;
			
			"""
			match = re.match(MSG_HAS_LOGGED_IN, con);
			if( match ):
				for p in engine.players:
					if( p.gid ): continue;
					if( removeColors(p.name) == match[1]):
						p.gid = match[2];
			"""
	
	if( msg.descriptor == 9 ): # center message
		cen_raw = msg.getStr();
		if(cen_raw):
			cen = removeColors(cen_raw);
			#print(cen, file=sys.stderr);
			state.centerMessage = cen;
			state.centerMessageRaw = cen_raw;
			match = re.match(CEN_MATCH_WINNER, cen);
			if( match ):
				for t in engine.teams:
					if( removeColors(t.name) == match[1] ):
						state.matchWinner = t;
			
			match = re.match(CEN_ROUND_WINNER, cen);
			if( match ):
				for t in engine.teams:
					if( removeColors(t.name) == match[1] ):
						state.roundWinner = t;
	
	
	if( msg.descriptor == 20 ): #ongetid
		global gotIDs;
		if(not gotIDs):
			_id = msg.getShort()+(msg.getShort()-1);
			p = Player(_id);
			NetObj.objs[_id] = p;
			engine.players.append(p);
			gotIDs = True;
	
	
	if( msg.descriptor == 24 ): # object sync
		_id = msg.getShort();
		obj = NetObj.objs.get(_id);
		if( obj ):
			obj.readNet(msg);
			state.obj = obj;
			state.objIsSync = True;
	
	if( msg.descriptor == 22 or msg.descriptor == 202 ): # object destroy or player remove
		while(True):
			_id = msg.getShort();
			
			if(not _id):
				break;
			
			if( NetObj.objs.get(_id) ):
				NetObj.objs[_id].onDestroy();
				del NetObj.objs[_id];
	
	
	if( msg.descriptor == 201 ): # new player
		p = Player();
		p.readNetInit(msg);
		engine.players.append(p);
		
		state.obj = p;
		state.objIsNew = True;
	
	if( msg.descriptor == 330 ): # new AI
		p = Player();
		p.AI = True;
		p.readNetInit(msg);
		engine.players.append(p);
		
		state.obj = p;
		state.objIsNew = True;
	
	if( msg.descriptor == 220 or msg.descriptor == 331 ): # new team
		t = Team();
		t.readNetInit(msg);
		engine.teams.append(t);
		
		state.obj = t;
		state.objIsNew = True;
	
	"""
	if( msg.descriptor == 320 ): # new cycle
		c = Cycle();
		c.readNetInit(msg);
		engine.cycles.append(c);
	"""
	
	#print(msg.getStr());
	
	#print(nums);
	
	return state;

