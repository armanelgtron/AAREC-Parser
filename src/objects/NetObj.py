
class NetObj:
	# static variable
	objs = {};
	
	def onDestroy(this):
		pass;
	
	def readNetInit(this, msg):
		this.id = msg.getShort();
		this.ownerid = msg.getShort();
		NetObj.objs[this.id] = this;
		this.readNet(msg);
	
	def readNet(this, msg):
		pass;
