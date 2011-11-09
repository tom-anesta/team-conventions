from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionSphere

#from pandac.PandaModules import CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue

from pandac.PandaModules import BitMask32
import math

from projectile import Projectile

class Bullet(Projectile):
	def __init__(self, game = None, parent = None, vel = Vec3()):
		models = MODELS_PATH + "SleekCraft"
		anims = {}
		
		Projectile.__init__(self, models, anims, "**/CollisionSphere", game, parent, parent.getPos(), vel)
	
