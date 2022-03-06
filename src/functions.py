
import re

REGEX_COLORS = r"0x([0-9A-Fa-f]{6}|RESETT)(.*?)(?=0x(?:[0-9A-Fa-f]{6}|RESETT)|$)";
def removeColors(_str):
	return re.sub(REGEX_COLORS, r"\2", _str);

def filterStr(_str): #! Filter illegal player characters. Heavily based on ArmagetronAd's filtering.
	out = "";
	for i in _str:
		char = ord(i);
		if(char <= 126 and char > 32): # Leave ASCII characters but convert them to lower case
			if(char == 48):
				out += "o"; # map 0 to o because z-man
			else:
				out += i.lower();
		
		# map umlauts and similar to their base characters
		elif(char >= 0xc0 and char <= 0xc5): out += 'a';
		elif(char >= 0xd1 and char <= 0xd6): out += 'o';
		elif(char >= 0xd9 and char <= 0xdD): out += 'u';
		elif(char == 0xdf): out += 's';
		elif(char >= 0xe0 and char <= 0xe5): out += 'a';
		elif(char >= 0xe8 and char <= 0xeb): out += 'e';
		elif(char >= 0xec and char <= 0xef): out += 'i';
		elif(char >= 0xf0 and char <= 0xf6): out += 'o';
		elif(char >= 0xf9 and char <= 0xfc): out += 'u';
		elif(char >= 0xc0 and char <= 0xc5): out += 'a';
		else:
			# some of those are a bit questionable, but still better than lots of underscores
			c = ({
				161: '!',
				162: 'c',
				163: 'l',
				165: 'y',
				166: '|',
				167: 's',
				168: '"',
				169: 'c',
				170: 'a',
				171: '"',
				172: '!',
				174: 'r',
				176: 'o',
				177: '+',
				178: '2',
				179: '3',
				182: 'p',
				183: '.',
				185: '1',
				187: '"',
				198: 'a',
				199: 'c',
				208: 'd',
				209: 'n',
				215: 'x',
				216: 'o',
				221: 'y',
				222: 'p',
				231: 'c',
				241: 'n',
				247: '/',
				248: 'o',
				253: 'y',
				254: 'p',
				255: 'y',
			}).get(char);
			if( c ):
				out += c;
			else:
				out += "_";
			
	return out;

def void(*a):
	pass;
