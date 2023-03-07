#!/usr/bin/python3


import sys, os;
import ctypes;
import re;
import time
import json


_MODE_STATS = 1;
_MODE_SCORES = 2;
_MODE_MESSAGES = 3;

MODES_STR = {
	"stats": _MODE_STATS,
	"score": _MODE_SCORES, "scores": _MODE_SCORES,
	"messages": _MODE_MESSAGES,
};

mode = 0;

from src.functions import *

from src.nMessage import *
from src.objects.netObjects import *

from src.Stats import Stats

from src.aarecParser import *


# static class, set properties directly
class engine:
	players = [];
	teams = [];
	cycles = [];

objSetEngine(engine);
aarecSetEngine(engine);


import argparse;
class argumentsParse(argparse.ArgumentParser):
	def __init__(this):
		argparse.ArgumentParser.__init__(this,
			description="Parse AAREC Recordings to get information about and from them");
		
		this.add_argument("file", metavar="FILE", type=str,
			help="path to AAREC file");
		
		this.add_argument("-o", "--out", dest="out",
			help="output file");
		
		this.add_argument("--human", dest="human", action="store_const", const=True,
			help="use human-friendly output");
		
		this.add_argument("--json", dest="json", action="store_const", const=True,
			help="use JSON output");
		
		this.add_argument("-m", "--mode", dest="mode", default=_MODE_SCORES,
			help="the mode to use. stats|score");
		
		this.add_argument("--show-percentage", dest="perc", action="store_true",
			help="write the percentage of aarec read"
		);
	
	def parse(this, argv):
		return vars(this.parse_args(argv));


def main(argv):
	
	parser = argumentsParse();
	args = parser.parse(argv);
	
	#print(args)
	
	global mode;
	try:
		try:
			mode = int(args["mode"]);
		except ValueError:
			mode = MODES_STR[args["mode"]];
	except:
		#parser.print_usage(file=sys.stderr);
		parser.error("invalid argument for mode");
		#print("Invalid argument for mode", file=sys.stderr);
		return;
	
	jsonOutput = False;
	humanOutput = False;
	
	if( args["json"] ):
		jsonOutput = True;
	else:
		humanOutput = True;
	
	
	showPercentage = args["perc"];
	
	f = None;
	
	ext = os.path.splitext(args["file"])[1];
	
	if( ext == ".gz" ):
		import gzip;
		f = gzip.open(args["file"], "rb");
	else:
		f = open(args["file"], "rb");
	
	
	
	startTime = time.time();
	
	if( showPercentage ):
		print("Please wait...", end="", file=sys.stderr, flush=True);
		endTimeState = seekGetLastAARECTime(f).time;
		print("\033[1K", end="\r", file=sys.stderr, flush=True);
		f.seek(0);
		stframe = 0;
	
	if( mode == _MODE_SCORES and jsonOutput ):
		print(end="[");
		dScoreOutp = False;
	
	if( mode == _MODE_STATS ):
		stats = Stats();
	
	if( mode == _MODE_MESSAGES and jsonOutput ):
		parser.error("JSON output is not supported for messages mode");
		return;
	
	for state in parseAAREC(f):
		if( showPercentage ):
			stframe += 1;
			if( stframe%10000 == 0 ):
				print("\033[2K", end="", file=sys.stderr);
				print(int(( 100 * state.time ) / endTimeState), "%", end="\r", file=sys.stderr, flush=True);
		#print(state)
		
		if( mode == _MODE_STATS ):
			if( state.chatMessage is not None ):
				chat = state.chatMessage; p = state.player;
				#print(chat, file=sys.stderr);
				stats.chats += 1; p.stats.chats += 1;
				if( chat.lower().find("lol") != -1 ):
					stats.lols += 1; p.stats.lols += 1;
		
		if( mode == _MODE_MESSAGES ):
			if( state.chatMessage ):
				print( "[T="+str(state.time)+"]", state.chatMessage );
			if( state.consoleMessage is not None ):
				print( "[T="+str(state.time)+"]", state.consoleMessage );
		
		if( state.matchWinner ):
			if( mode == _MODE_SCORES ):
				
				if( humanOutput ):
					print("Match winner:", state.matchWinner.name);
					print("Time:", state.time);
					
					#print("Teams:");
					print( str.ljust("Teamname", 16), str.rjust("Score", 6) );
					print( str.ljust("¯¯¯¯¯¯¯¯", 16), str.rjust("¯¯¯¯¯", 6) );
					for t in sorted(engine.teams, key=lambda t:t.score, reverse=True):
						print( str.ljust(t.name, 16), str(t.score).rjust(6) );
					
					print(); print();
					
					spectators = [];
					#print("Players:");
					print( str.ljust("Player", 16), str.rjust("Score", 6), str.ljust("Team", 16), sep="  " );
					print( str.ljust("¯¯¯¯¯¯", 16), str.rjust("¯¯¯¯¯", 6), str.ljust("¯¯¯¯", 16), sep="  " );
					for p in sorted(engine.players, key=lambda p:p.score, reverse=True):
						if( p.team ):
							print( str.ljust(p.name, 16), str(p.score).rjust(6), str.ljust(p.team.name, 16), sep="  " );
						else:
							if( p.teamID ):
								spectators.append(p.name+" (error)");
							else:
								spectators.append(p.name);
					
					print();
					print("Spectators:", str.join(", ", spectators));
					
					print();
				
				elif( jsonOutput ):
					if( showPercentage ): print("\033[2K", end="", file=sys.stderr, flush=True);
					if( dScoreOutp ):
						print(end=",");
					else:
						dScoreOutp = True;
					
					jsonLines = json.dumps({
						"winner": ( state.matchWinner and state.matchWinner.name ),
						"teams": {
							t.name: t.score
							for t in sorted(engine.teams, key=lambda t:t.score, reverse=True)
						},
						"players": {
							p.name: {
								"score": p.score,
								"team": (p.team and p.team.name)
							}
							for p in sorted(engine.players, key=lambda p:p.score, reverse=True) 
						},
					}, indent=2).split("\n");
					
					for line in jsonLines:
						print(end="\n  "+line);
					
					if( showPercentage ): print(file=sys.stderr, flush=True);
	
	
	if( mode == _MODE_SCORES and jsonOutput ):
		if( showPercentage ): print("\033[2K", end="", file=sys.stderr, flush=True);
		print("\n]");
	
	if( mode == _MODE_STATS ):
		Stats.byPlayer["TOTAL"] = stats;
		print(json.dumps({s: (Stats.byPlayer[s].__dict__) for s in Stats.byPlayer}, indent=2));
	
	
	print("Recording time:", state.time, "seconds", file=sys.stderr);
	print("Parsing took", round( time.time() - startTime, 6 ), "seconds", file=sys.stderr);
	
	f.close();


if(__name__ == "__main__"):
	main(list(sys.argv[1:]));
