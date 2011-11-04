from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
import math

class Collidable(Actor):
	def __init__(self, models = None, anims = None, damages = false):
		Actor.__init__(self, models, anims)
		
		
