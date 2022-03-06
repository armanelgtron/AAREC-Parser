
from src.objects.Color import Color

from src.functions import *
from src.Stats import Stats


from src.objects.NetObj import NetObj

from src.objects.Player import Player
from src.objects.Team import Team
from src.objects.Cycle import Cycle


def objSetEngine(e):
	global engine; engine = e;
	Player.setEngine(e);
	Team.setEngine(e);
	Cycle.setEngine(e);
	return e;
