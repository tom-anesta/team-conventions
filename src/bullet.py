from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
import math

from projectile import Projectile

class Bullet(Projectile):
	def __init__(self, game = None, parent = None, vel = Vec3()):
		models = MODELS_PATH + "Bullet"
		anims = {}
		
		vel.normalize()
		vel *= 24
		
		Projectile.__init__(self, models, anims, "**/CollisionSphere", game, parent, parent.getPos(), vel)
	
