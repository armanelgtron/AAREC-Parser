
import math
import ctypes

class nMessage:
	
	def __init__(this, descriptor,id=False,alloc=False):
		this.len = 0;
		
		this.id = id;
		this.bufpos = 0;
		
		this.buf = descriptor;
	
	
	def getHeader(this):
		this.descriptor = this.getShort();
		this.id = this.getShort();
		this.len = this.getShort();
		
		this.buf = this.buf[this.bufpos:this.bufpos+(this.len*2)];
		this.bufpos = 0;
	
	def getChar(this):
		#return this.buf[this.bufpos++];
		try:
			val = this.buf[this.bufpos];
		except IndexError:
			val = 0;
		this.bufpos += 1;
		return val;
	
	def getShort(this):
		a = this.getChar(); b = this.getChar();
		return (a<<8)|b;
	
	def getUInt(this):
		a = this.getShort(); b = this.getShort();
		return (b<<16)|a;
	
	def getInt(this):
		return ctypes.c_int32(this.getUInt()).value;
	
	def getFloat(this):
		trans = this.getInt();
		mant = trans & (1 << 25) - 1;
		negative = trans & 1 << 25;
		exp = trans - mant - negative >> 26;
		x = float(mant) / (1 << 25);
		
		if (negative): x = -x;
		
		while( exp >= 6 ):
			exp -= 6;
			x *= 64.0;
		
		while( exp > 0 ):
			exp -= 1;
			x *= 2.0;
		
		return x;
	
	def getBool(this):
		return this.getShort()!=0;
	
	def getStr(this):
		return this.getString();
	
	def getString(this):
		_len = math.ceil(this.getShort()/2);
		c1, c2 = 0, 0; _str="";
		for i in range(_len):
			c2 = this.getChar(); c1 = this.getChar();
			if(c1):
				_str += chr(c1);
				if(c2) :
					if(c1 > 0x7f):
						# needed to deal with characters causing
						# the next character to be the wrong char
						c2 = (c2+1)%0x100;
					
					_str += chr(c2);
		
		return _str;
	


