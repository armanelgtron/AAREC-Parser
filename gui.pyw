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
	global Qt, QtWidgets, QtGui, uic;
	
	if(version == 6):
		if(use_pyside):
			from PySide6 import QtWidgets, QtGui, QtUiTools;
			from PySide6 import QtCore as Qt;
		else:
			from PyQt6 import QtWidgets, QtGui, uic;
			from PyQt6 import QtCore as Qt;
	elif(version == 5):
		if(use_pyside):
			from PySide2 import QtWidgets, QtGui, QtUiTools;
			from PySide2 import QtCore as Qt;
		else:
			from PyQt5 import QtWidgets, QtGui, uic;
			from PyQt5 import QtCore as Qt;
	elif(version == 4):
		if(use_pyside):
			from PySide import QtGui as QtWidgets;
			from PySide import QtGui, QtUiTools;
			from PySide import QtCore as Qt;
		else:
			from PyQt4 import QtGui as QtWidgets;
			from PyQt4 import QtGui, uic;
			from PyQt4 import QtCore as Qt;
	
	class Q:
		pass;
	
	if( version < 6 ):
		QtWidgets.QMessageBox.Icon.NoIcon = QtWidgets.QMessageBox.NoIcon;
		QtWidgets.QMessageBox.Icon.Information = QtWidgets.QMessageBox.Information;
		QtWidgets.QMessageBox.Icon.Warning = QtWidgets.QMessageBox.Warning;
		QtWidgets.QMessageBox.Icon.Critical = QtWidgets.QMessageBox.Critical;
		QtWidgets.QMessageBox.Icon.Question = QtWidgets.QMessageBox.Question;
		Qt.DropAction = Qt.Qt;
		Qt.FocusReason = Q();
		for c in Qt.Qt.__dict__:
			x = re.findall( "(.+)FocusReason", c );
			if( len(x) != 0 ):
				setattr( Qt.FocusReason, x[0], getattr(Qt.Qt, c) );
		Qt.Orientation = Qt.Qt;
	else:
		for c in Qt.Qt.ContextMenuPolicy:
			setattr(Qt.Qt,str(c).split(".")[1],c);
		Qt.DropAction = Qt.Qt.DropAction;
		for x in ( QtGui.QTextCursor.MoveOperation, QtGui.QTextCursor.SelectionType ):
			for c in x:
				setattr(QtGui.QTextCursor,str(c).split(".")[1],c);
		Qt.FocusReason = Qt.Qt.FocusReason;
		for c in dict(Qt.Qt.FocusReason.__dict__):
			x = re.findall( "(.+)FocusReason", c );
			if( len(x) != 0 ):
				setattr( Qt.FocusReason, x[0], getattr(Qt.FocusReason, c) );
		Qt.Orientation = Qt.Qt.Orientation;
		for c in dict(QtGui.QTextDocument.FindFlag.__dict__):
			setattr( QtGui.QTextDocument, c, getattr(QtGui.QTextDocument.FindFlag, c) );
	
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
				gui = loader.load(f);
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
qtPrefPySide = False;


import argparse;
class argumentsParse(argparse.ArgumentParser):
	def __init__(this):
		argparse.ArgumentParser.__init__(this,
			description="Parse AAREC Recordings to get information about and from them (GUI version)");
		
		this.add_argument("file", metavar="FILE", type=str, nargs='?',
			help="path to AAREC file. Currently supports .aarec (of course), .zip, and .gz");
		
		this.add_argument("-qt", dest="qt", type=int,
			#help="specify which version of qt to try to use");
			help=argparse.SUPPRESS);
		
		this.add_argument("--use-pyside", dest="pyside", action="store_true",
			#help="whether or not to try to use pyside instead of pyqt");
			help=argparse.SUPPRESS);
		
	def parse(this, argv):
		return vars(this.parse_args(argv));

if( __name__ == "__main__" ):
	parser = argumentsParse();
	args = parser.parse(sys.argv[1:]);
	
	if( args["pyside"] is not None ):
		qtPrefPySide = args["pyside"];
	if( args["qt"] is not None ):
		qtVersions = [ args["qt"] ];


qtCollectedErrors = [];

if( not qtImportOverride ):
	# try base PyQt
	for v in qtVersions:
		try:
			importPyQt( v, qtPrefPySide );
		except ImportError as exc:
			qtCollectedErrors.append(exc);
		else:
			qtImported = v;
			break;

	# try again, but try PySide instead
	if( not qtImported ):
		for v in qtVersions:
			try:
				importPyQt( v, ( not qtPrefPySide ) );
			except ImportError as exc:
				qtCollectedErrors.append(exc);
			else:
				qtImported = v;
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


# based on https://stackoverflow.com/a/8735509
def isValidForXML(ch):
	c = ord(ch);
	return (
		0x20 <= c <= 0xD7FF or
		0xE000 <= c <= 0xFFFD or
		0x10000 <= c <= 0x10FFFF or
		c in (0x9, 0xA, 0xD)
	);

def filterStr(s):
	return str.join('', filter(isValidForXML, str(s)));


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
			this.aarecLoadSafe( fileInfo );
	
	def aarecLoadSafe(this, fileInfo):
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
			
			sState = {};
			sState["scoreRq"] = False;
			
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
					name = filterStr( t["name"] ); score = str(t["score"]);
					if( t["numPlayers"] <= 0 ):
						name = E.S( filterStr( t["name"] ) );
						#score = E.S( score );
					teamScoreBoard.append(E.TR(
						E.TD( name ), E.TD( score, align="right" )
					));
				
				for p in data["players"]:
					if( p["team"] or p["score"] ):
						if( p["team"] ): team = filterStr(p["team"]);
						elif( p["teamID"] ): team = E.I("error");
						else: team = E.I("spec");
						playerScoreBoard.append(E.TR(
							E.TD(filterStr(p["name"])), E.TD(str(p["score"]), align="right"), E.TD( team )
						));
					else:
						if( p["teamID"] ):
							spectators.append(p["name"]+" (error)");
						else:
							spectators.append(p["name"]);
				
				if( sState["scoreRq"] ):
					sState["scoreRq"] = False;
					this.scoresBrowser.append("");
				
				this.scoresBrowser.append(getHTML(
						E.DIV(
							E.P("Time: "+str(data["time"])),
							E.P("Winner: "+filterStr(data["winner"])),
							teamScoreBoard,
							playerScoreBoard,
							E.P("Spectators: "+filterStr(str.join(", ", spectators))),
						)
					)
				);
				this.scoresBrowser.append("");
			this.worker.scoreboard.connect(appendScoreBoard);
			
			def scoreRq( time, type_, name, score ):
				if( score and type_ != "Team" ):
					old = this.scoresBrowser.textCursor();
					cur = this.scoresBrowser.textCursor();
					cur.movePosition( QtGui.QTextCursor.Start );
					cur.movePosition( QtGui.QTextCursor.NextBlock );
					cur.movePosition( QtGui.QTextCursor.NextBlock );
					cur.select( QtGui.QTextCursor.LineUnderCursor );
					this.scoresBrowser.setTextCursor(cur);
					
					this.scoresBrowser.append(getHTML(
						(E.SPAN(
							"[%s] %s %s left with %i points" % (
								str(time), type_, filterStr(name), score
							), style="line-height:100%"
						))
					));
					
					this.scoresBrowser.setTextCursor(old);
					sState["scoreRq"] = True;
			
			this.worker.scoreRq.connect(scoreRq);
			
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
		uic.loadUi( os.path.join( os.path.dirname(__file__), "gui", "main.ui" ), this );
		
		this.progTitle = "AAREC-Parser";
		this.setWindowTitle(this.progTitle);
		
		this.setAcceptDrops(True);
		
		this.thread = None;
		this.threadStop = None;
		
		
		this.progressBar.setValue(0);
		this.progressBar.hide();
		
		this.statusBar().showMessage("No file loaded.");
		
		this.tabs.removeTab(this.tabs.indexOf(this.mapTab));
		this.tabs.removeTab(this.tabs.indexOf(this.statsTab));
		
		
		this.actionOpen.triggered.connect( this.aarecOpen );
		
		
		if( qtImported >= 6 ):
			this.actionFind = QtGui.QShortcut( QtGui.QKeySequence.StandardKey.Find, this, this.openFind );
		else:
			this.actionFind = QtWidgets.QShortcut( QtGui.QKeySequence.Find, this, this.openFind );
		
		this.findHide.clicked.connect(this.closeFind);
		this.findText.textChanged.connect(lambda:this.find(begin=True))
		this.findPrev.clicked.connect(lambda:this.find(prev=True, active=True));
		this.findNext.clicked.connect(lambda:this.find(prev=False, active=True));
		
		this.closeFind();
		
		this.cfgTextBrowser(this.messages);
		this.cfgTextBrowser(this.scoresBrowser);
		
		this.toolBar.orientationChanged.connect( this.confTabs );
		
		
		this.show();
		
		
		if( args["file"] is not None ):
			loadFileSoon = Qt.QTimer();
			loadFileSoon.setSingleShot( True );
			print( args["file"] );
			loadFileSoon.timeout.connect(lambda:this.aarecLoad( [ args["file"] ] ));
			loadFileSoon.start(1);
			this.loadFileSoon = loadFileSoon;
	
	def cfgTextBrowser(this, tb):
		tb.setContextMenuPolicy(Qt.Qt.CustomContextMenu);
		tb.customContextMenuRequested.connect(lambda e:this.textBrowserContextMenu(tb, e));
	def textBrowserContextMenu(this, tb, e):
		menu = tb.createStandardContextMenu();
		menu.addSeparator();
		find = menu.addAction("Find");
		find.setShortcut( QtGui.QKeySequence(QtGui.QKeySequence.Find) );
		a = menu.exec(tb.mapToGlobal(e));
		if( a == find ):
			this.openFind();
	
	def confTabs(this):
		this.tabs.setDocumentMode( 
			this.toolBar.orientation() == Qt.Orientation.Horizontal and
			this.findWidget.isHidden() and
		1);
	
	def openFind(this):
		this.findWidget.show();
		this.findText.setFocus( Qt.FocusReason.Other );
		this.findText.selectAll();
		this.confTabs();
	
	def closeFind(this):
		this.findWidget.hide();
		this.confTabs();
	
	def find(this, begin=False, prev=False, active=False):
		find = this.findText.text();
		textBrowser = None;
		options = QtGui.QTextDocument.FindFlag(0);
		
		if( prev ): options |= QtGui.QTextDocument.FindBackward;
		if( this.caseSensitive.isChecked() ): options |= QtGui.QTextDocument.FindCaseSensitively;
		
		if( this.findOptions.currentIndex() == 1 ):
			diacritic = "ŠŒŽšœžŸ¥µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýÿ¡¿";
			diacriticMap = ["S","OE","Z","s","oe","z","Y","Y","u","A","A","A","A","A","A","AE","C","E","E","E","E","I","I","I","I","D","N","O","O","O","O","O","O","U","U","U","U","Y","s","a","a","a","a","a","a","ae","c","e","e","e","e","i","i","i","i","o","n","o","o","o","o","o","o","u","u","u","u","y","y","!","?"];
			
			txt = re.escape(find);
			new = "";
			for c in txt:
				i = 0; rg = [];
				for x in range(diacriticMap.count( c )):
					try:
						l = diacriticMap.index( c, i );
					except ValueError:
						pass;
					else:
						rg.append(diacritic[l]);
						i = l+1;
				if( len(rg) == 0 ):
					new += c;
				else:
					rg.insert(0, c);
					new += "("+str.join("|", rg)+")";
			
			#print(new);
			find = Qt.QRegularExpression( new );
			
		elif( this.findOptions.currentIndex() == 2 ):
			options |= QtGui.QTextDocument.FindWholeWords;
		elif( this.findOptions.currentIndex() == 3 ):
			find = Qt.QRegularExpression( find );
		
		if( this.tabs.currentWidget() == this.scoresTab ):
			textBrowser = this.scoresBrowser;
		elif( this.tabs.currentWidget() == this.msgTab ):
			textBrowser = this.messages;
		
		worked = False;
		
		if( textBrowser ):
			if( begin ):
				cur = textBrowser.textCursor()
				cur.setPosition( cur.selectionStart() );
				cur.movePosition(QtGui.QTextCursor.Left);
				textBrowser.setTextCursor(cur);
			worked = textBrowser.find( find, options );
			if( ( not worked ) and ( begin or this.findWrap.isChecked() ) ):
				cur = textBrowser.textCursor()
				if( prev ):
					cur.movePosition(QtGui.QTextCursor.End);
				else:
					cur.movePosition(QtGui.QTextCursor.Start);
				textBrowser.setTextCursor(cur);
				worked = textBrowser.find( find, options );
			if( active ):
				textBrowser.setFocus( Qt.FocusReason.Other );
		
		if( worked or ( this.findText.text() == "" ) ):
			this.findText.setStyleSheet("");
		else:
			sel = textBrowser.textCursor().selectedText();
			red = True;
			if( isinstance(find, Qt.QRegularExpression) ):
				#if( find.match(sel).hasMatch() ):
				#	red = False;
				flags = re.RegexFlag(0);
				if( not this.caseSensitive.isChecked() ):
					flags |= re.IGNORECASE;
				if( re.match( find.pattern(), sel, flags ) ):
					red = False;
			elif( find == sel or ( not this.caseSensitive.isChecked() and find.lower() == sel.lower() ) ):
				red = False;
			if( red ):
				this.findText.setStyleSheet("background:red");
			else:
				this.findText.setStyleSheet("background:#ff0");
	
	
	def dragEnterEvent(this, e):
		if( e.mimeData().hasUrls() ):
			e.accept();
		else:
			super().dragEnterEvent(e);
	
	def dragMoveEvent(this, e):
		if( e.mimeData().hasUrls() ):
			e.setDropAction(Qt.DropAction.CopyAction)
			e.accept();
		else:
			super().dragMoveEvent(e);
	
	def dropEvent(this, e):
		if( e.mimeData().hasUrls() ):
			this.aarecLoadSafe( [ e.mimeData().urls()[0].path() ] );


class Worker(Qt.QObject):
	finished = Qt.Signal();
	progress = Qt.Signal(int);
	message = Qt.Signal(float, str);
	status = Qt.Signal(str);
	scoreboard = Qt.Signal(dict);
	scoreRq = Qt.Signal(float, str, str, int);

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
		try:
			# there should be a time event somewhere in the last 4K bytes, surely
			f.seek(-4096, 2);
		except OSError:
			pass;
		endTimeState = seekGetLastAARECTime(this.f).time;
		if( endTimeState == 0 ):
			endTimeState = 0.0000001;
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
			
			if( state.objIsDel ):
				print( state.obj.__class__.__name__ );
				try: state.obj.name; state.obj.score;
				except AttributeError: pass;
				else:
					this.scoreRq.emit( 
						state.time, 
						state.obj.__class__.__name__, 
						removeColors( state.obj.name ),
						state.obj.score,
					);
			
			if( state.matchWinner ):
				this.scoreboard.emit({
					"winner": ( state.matchWinner and state.matchWinner.name ),
					"time": state.time,
					"teams": [
						{
							"name": removeColors( t.name ),
							"score": t.score,
							"numPlayers": sum( 1 for p in engine.players if p.teamID == t.id ),
						}
						for t in sorted(engine.teams, key=lambda t:t.score, reverse=True)
					],
					"players": [
						{
							"name": removeColors( p.name ),
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
	import signal;
	signal.signal(signal.SIGINT, signal.SIG_DFL);
	
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
