#!/usr/bin/python3


import sys, os;
import ctypes;
import re;
import time
import html;

import lxml;
from lxml.html import builder as E;
def getHTML(e):
	return lxml.html.tostring(e).decode();


# function to deal with the various versions of PyQt and their differences
def importPyQt(version=5,use_pyside=False):
	global Qt, QtWidgets, uic;
	
	if(version == 6):
		if(use_pyside):
			from PySide6 import QtWidgets, QtUiTools;
			from PySide6 import QtCore as Qt;
		else:
			from PyQt6 import QtWidgets, uic;
			from PyQt6 import QtCore as Qt;
	elif(version == 5):
		if(use_pyside):
			from PySide2 import QtWidgets, QtUiTools;
			from PySide2 import QtCore as Qt;
		else:
			from PyQt5 import QtWidgets, uic;
			from PyQt5 import QtCore as Qt;
	elif(version == 4):
		if(use_pyside):
			from PySide import QtGui as QtWidgets;
			from PySide import QtUiTools;
			from PySide import QtCore as Qt;
		else:
			from PyQt4 import QtGui as QtWidgets;
			from PyQt4 import uic;
			from PyQt4 import QtCore as Qt;
	
	if( version < 6 ):
		QtWidgets.QMessageBox.Icon.NoIcon = QtWidgets.QMessageBox.NoIcon;
		QtWidgets.QMessageBox.Icon.Information = QtWidgets.QMessageBox.Information;
		QtWidgets.QMessageBox.Icon.Warning = QtWidgets.QMessageBox.Warning;
		QtWidgets.QMessageBox.Icon.Critical = QtWidgets.QMessageBox.Critical;
		QtWidgets.QMessageBox.Icon.Question = QtWidgets.QMessageBox.Question;
	else:
		for c in Qt.Qt.ContextMenuPolicy:
			setattr(Qt.Qt,str(c).split(".")[1],c);
	
	if( ( use_pyside and version <= 5 ) or version < 5 ):
		QtWidgets.QApplication.exec = QtWidgets.QApplication.exec_;
		QtWidgets.QMenu.exec = QtWidgets.QMenu.exec_;
	
	if(use_pyside):
		# basic uic implementation
		class uic:
			@staticmethod
			def loadUi(fileName, widget):
				# basic loading from file
				loader = QtUiTools.QUiLoader();
				f = Qt.QFile(fileName);
				f.open(Qt.QFile.ReadOnly);
				gui = loader.load(fileName);
				f.close();
				
				# loop through all widgets and assign vars
				def recurChildren(m):
					for w in m.children():
						setattr(widget, w.objectName(), w);
						recurChildren(w);
				recurChildren(gui);
				
				widget.resize(gui.size());
				gui.statusBar().hide();
				
				widget.setCentralWidget(gui);
	else:
		Qt.Signal = Qt.pyqtSignal;
		Qt.Slot = Qt.pyqtSlot;


qtImported = False;
qtImportOverride = False;
qtVersions = [5,6,4];

qtCollectedErrors = [];

if( not qtImportOverride ):
	# try base PyQt
	for v in qtVersions:
		try:
			importPyQt(v);
		except ImportError as exc:
			qtCollectedErrors.append(exc);
		else:
			qtImported = True;
			break;

	# try again, but try PySide instead
	if( not qtImported ):
		for v in qtVersions:
			try:
				importPyQt(v, True);
			except ImportError as exc:
				qtCollectedErrors.append(exc);
			else:
				qtImported = True;
				break;

if( not qtImported ):
	error = [
		"Error while loading PyQt",
		"All attempts at loading PyQt have failed.",
	];
	errs = str(qtCollectedErrors);
	
	for l in error:
		print(l, file=sys.stderr);
	
	print(file=sys.stderr);
	
	print("Errors:", file=sys.stderr);
	for e in qtCollectedErrors:
		print(str(e), file=sys.stderr);
	
	try:
		from tkinter import messagebox
	except ImportError:
		os.system("xmessage '"+str.join("\n", error).replace("'","`")+"'");
	else:
		messagebox.showerror(error[0], str.join("\n", error[1:]));
	exit();


from src.functions import *

from src.nMessage import *
from src.objects.netObjects import *

from src.Stats import Stats

from src.aarecParser import *



gzipSupported = True;
try:
	import gzip;
except ImportError:
	gzipSupported = False;

zipSupported = True;
try:
	import zipfile;
except ImportError:
	zipSupported = False;


def colorCodeUsed(text):
	return bool(re.search(REGEX_COLORS, text));

def htmlColor(_str,
	whiteIsRESETT=True,
	colorStyle="background:black",
	darkColorStyle="background:white",
):
	#return re.sub(REGEX_COLORS, r"<font color='#\1'>\2</font>", _str);
	colors = re.findall(REGEX_COLORS, "0xRESETT"+_str);
	out = "";
	for c in colors:
		if( c[0] == "RESETT" or ( whiteIsRESETT and c[0] == "ffffff" ) ):
			out += html.escape(c[1]);
		else:
			cl = int(float.fromhex(c[0]));
			r = (cl&0xff0000) / 0xff0000;
			g = (cl&0x00ff00) / 0x00ff00;
			b = (cl&0x0000ff) / 0x0000ff;
			if( ( r < 0.5 and g < 0.5 and b < 0.5 ) or ( r+g+b < 0.7 ) ):
				style = darkColorStyle;
			else:
				style = colorStyle;
			#rgb"+str((int(r*255),int(g*255),int(b*255)))+"
			out += "<font color='#"+c[0]+"' style='"+style+"'>"+html.escape(c[1]).replace("  ", " &nbsp;")+"</font>";
	return out;


class Main(QtWidgets.QMainWindow):
	def aarecOpen(this):
		fileTypes = [
			"All supported (*.aarec *.zip *.gz)",
			"Armagetron Advanced Recordings (*.aarec)",
			"Compressed Files (*.zip *.gz)",
			"All Files (*.*)" # should always be last
		];
		fileInfo = QtWidgets.QFileDialog.getOpenFileName( this, "Load AAREC", "", str.join(";;", fileTypes) );
		
		if( fileInfo[0] ):
			if( this.thread ):
				this.thread.requestInterruption();
				
				if( not this.threadStop ):
					this.threadStop = Qt.QTimer();
					
					def check():
						if( not ( this.thread and this.thread.isRunning() ) ):
							this.threadStop.stop();
							this.threadStop = None;
							this.aarecLoad( fileInfo );
					
					this.threadStop.timeout.connect(check);
					
					this.threadStop.start(1000);
			else:
				this.aarecLoad( fileInfo );
	
	def aarecLoad(this, fileInfo):
		if( True ):
			this.setWindowTitle( os.path.basename(fileInfo[0])+" - "+this.progTitle );
			
			this.thread = Qt.QThread();
			this.worker = Worker(fileInfo[0]);
			this.worker.moveToThread(this.thread);
			this.worker.fatalError.connect(gui_exception);
			this.thread.started.connect(this.worker.run);
			
			this.worker.status.connect(this.statusBar().showMessage);
			
			# prepare progressbar
			this.progressBar.show();
			this.worker.progress.connect(this.progressBar.setValue);
			
			# prepare message log output
			this.messages.setText("");
			# set color output background depending on color scheme
			if( this.messages.palette().base().color().value() > 160 ):
				def htmlColorCust(msg):
					return htmlColor(msg,darkColorStyle="");
			elif( this.messages.palette().base().color().value() < 96 ):
				def htmlColorCust(msg):
					return htmlColor(msg,colorStyle="");
			else:
				htmlColorCust = htmlColor;
			this.worker.message.connect(lambda time, msg: this.messages.append("["+str(time)+"] <span>"+htmlColorCust(msg)+"</span>"));
			
			this.scoresBrowser.setText("");
			def appendScoreBoard(data):
				spectators = [];
				
				def TH(*text):
					return E.TH(align="left", *text);
				
				teamScoreBoard = E.TABLE(E.TR( 
					TH("Teamname"), TH("Score")
				));
				
				playerScoreBoard = E.TABLE(E.TR(
					TH("Player"), TH("Score"), TH("Team")
				));
				
				for t in data["teams"]:
					teamScoreBoard.append(E.TR(
						E.TD(t["name"]), E.TD(str(t["score"]), align="right")
					));
				
				for p in data["players"]:
					if( p["team"] ):
						playerScoreBoard.append(E.TR(
							E.TD(p["name"]), E.TD(str(p["score"]), align="right"), E.TD(p["team"])
						));
					else:
						if( p["teamID"] ):
							spectators.append(p["name"]+" (error)");
						else:
							spectators.append(p["name"]);
				
				this.scoresBrowser.append(getHTML(
						E.DIV(
							E.P("Time: "+str(data["time"])),
							E.P("Winner: "+str(data["winner"])),
							teamScoreBoard,
							playerScoreBoard,
							E.P("Spectators: "+str.join(", ", spectators)),
						)
					)
				);
				this.scoresBrowser.append("");
			this.worker.scoreboard.connect(appendScoreBoard);
			
			
			this.worker.finished.connect(this.thread.quit);
			this.worker.finished.connect(this.worker.deleteLater);
			
			def onFinish():
				this.progressBar.hide();
				this.thread.deleteLater();
				this.thread=None;
				#print(this.scoresBrowser.toHtml())
			
			this.thread.finished.connect(onFinish);
			
			this.thread.start();
	
	def __init__(this):
		super(Main, this).__init__();
		uic.loadUi("./gui/main.ui", this);
		
		this.progTitle = "AAREC-Parser";
		this.setWindowTitle(this.progTitle);
		
		this.thread = None;
		this.threadStop = None;
		
		
		this.progressBar.setValue(0);
		this.progressBar.hide();
		
		this.statusBar().showMessage("No file loaded.");
		
		this.tabs.removeTab(this.tabs.indexOf(this.mapTab));
		this.tabs.removeTab(this.tabs.indexOf(this.statsTab));
		
		
		this.actionOpen.triggered.connect( this.aarecOpen );
		
		this.show();


class Worker(Qt.QObject):
	finished = Qt.Signal();
	progress = Qt.Signal(int);
	message = Qt.Signal(float, str);
	status = Qt.Signal(str);
	scoreboard = Qt.Signal(dict);

	fatalError = Qt.Signal(object, object, object);

	def __init__(this, fileName):
		super(Worker, this).__init__();
		ext = os.path.splitext(fileName)[1];
		if( ext == ".gz" ):
			this.f = gzip.open(fileName, "rb");
		elif( ext == ".zip" ):
			with zipfile.ZipFile(fileName, "r") as z:
				for fi in z.filelist:
					if( os.path.splitext(fi.filename)[1] == ".aarec" ):
						this.f = z.open(fi, "r");
						break;
		else:
			this.f = open(fileName, "rb");

	def run(this):
		
		# set environment
		class engine:
			players = [];
			teams = [];
			cycles = [];
		
		objSetEngine(engine);
		aarecSetEngine(engine);
		
		NetObj.objs.clear();
		
		
		startTime = time.time();
		
		f = this.f;
		
		# reset progress bar
		this.progress.emit(0);
		
		this.status.emit("Calculating...");
		
		# get end time
		f.seek(-4096, 2); # there should be a time event somewhere in the last 4K bytes, surely
		endTimeState = seekGetLastAARECTime(this.f).time;
		stframe = 0;
		
		f.seek(0);
		
		this.status.emit("Parsing...");
		done = "Done.";
		
		stats = Stats();
		
		timeCalc = time.time()+1;
		
		for state in parseAAREC(f):
			# show percentage
			stframe += 1;
			if( stframe%10000 == 0 ):
				if( Qt.QThread.currentThread().isInterruptionRequested() ):
					done = "Aborted.";
					break;
				
				this.progress.emit(int(( 100 * state.time ) / endTimeState));
				
				if( ( time.time() - timeCalc ) > 1 ):
					eta = round( ( ( time.time() - startTime ) * (endTimeState / state.time) ) - ( time.time() - startTime ) );
					this.status.emit("Parsing... ETA: "+str(eta)+" seconds");
					timeCalc = time.time();
			
			if( state.chatMessage is not None ):
				
				chat = state.chatMessage; p = state.player;
				this.message.emit(state.time, state.chatMessageRaw);
				
				stats.chats += 1; p.stats.chats += 1;
				if( chat.lower().find("lol") != -1 ):
					stats.lols += 1; p.stats.lols += 1;
				
				
			if( state.consoleMessage is not None ):
				this.message.emit(state.time, state.consoleMessageRaw);
			
			
			if( state.matchWinner ):
				this.scoreboard.emit({
					"winner": ( state.matchWinner and state.matchWinner.name ),
					"time": state.time,
					"teams": [
						{
							"name": t.name,
							"score": t.score,
						}
						for t in sorted(engine.teams, key=lambda t:t.score, reverse=True)
					],
					"players": [
						{
							"name": p.name,
							"score": p.score,
							"team": (p.team and p.team.name),
							"teamID": (p.teamID),
						}
						for p in sorted(engine.players, key=lambda p:p.score, reverse=True) 
					],
				});
		
		
		f.close();
		
		this.status.emit(done+" Parsed in "+str(round( time.time() - startTime, 6 ))+" seconds. Recording is "+str(state.time)+" seconds long.");
		
		this.finished.emit();


if(__name__ == "__main__"):
	app = QtWidgets.QApplication(sys.argv);
	window = Main();
	
	def handle_exception(exc, val, tb):
		sys.__excepthook__(exc, val, tb);
		if( app.instance().thread() == Qt.QThread.currentThread() ):
			try:
				window.thread.requestInterruption();
			except:
				pass;
			gui_exception(exc, val, tb);
		else:
			window.worker.fatalError.emit(exc, val, tb);
			time.sleep(1);
			window.worker.finished.emit();
	
	def gui_exception(exc, val, tb):
		import traceback;
		msg = QtWidgets.QMessageBox();
		msg.setIcon(QtWidgets.QMessageBox.Icon.Critical);
		msg.setText("<b>An internal error occurred.</b> <br /> This is probably a bug, please send a bug report.");
		msg.setInformativeText(str.join("\n", traceback.format_exception(exc, val, tb)));
		msg.setWindowTitle("Internal Error");
		msg.exec();
		
		#app.quit();
	
	sys.excepthook = handle_exception;
	
	app.exec();
