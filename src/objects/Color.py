class Color:
	def __init__(this, r=0, g=0, b=0):
		this.r, this.g, this.b = r, g, b;
	
	def readNet(this, msg):
		this.r = msg.getShort();
		this.g = msg.getShort();
		this.b = msg.getShort();
	
	def readNetF(this, msg):
		this.r = int(msg.getFloat()*15);
		this.g = int(msg.getFloat()*15);
		this.b = int(msg.getFloat()*15);
