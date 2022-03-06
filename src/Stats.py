class Stats:
	# static variable
	byPlayer = {};
	
	def __init__(this):
		this.lols = 0;
		this.chats = 0;
	
	@property
	def __dict__(this):
		return {
			"lols": this.lols,
			"chats": this.chats,
		};
	
	def __iter__(this):
		for key in this.__dict__:
			yield key;
