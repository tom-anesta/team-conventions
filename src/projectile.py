from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionSphere

#from pandac.PandaModules import CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue

from pandac.PandaModules import CollisionHandlerPusher
from pandac.PandaModules import BitMask32
import math

class Projectile(Actor):
	def __init__(self, models = None, anims = None, sphereString = "**/bulletCollisionSphere", game = None, parent = None, pos = Point3(), vel = Vec3()):
		Actor.__init__(self, models, anims)
		
		self.game = game
		
		self.damage = 1
		self.parent = parent
		
		self.radius = 0.4
		
		self.setPos(pos)
		self.vel = vel
		
		self.collisionNodePath = CollisionSphere(self.radius)
		self.collisionNodePath.node().setFromCollideMask(BitMask32.bit(0))
		self.collisionNodePath.node().setIntoCollideMask(BitMask32.allOff())
		
		self.groundSphereHandler = CollisionHandlerQueue()
		self.game.cTrav.addCollider(self.collisionNodePath, self.groundSphereHandler)
#		
#		self.collisionHandler = CollisionHandlerPusher()
#		self.collisionHandler.addCollider(self.collisionNodePath, self)
	
	def registerCollider(self, collisionTraverser):
#		collisionTraverser.addCollider(self.collisionNodePath, self.collisionHandler)
		pass
	
	def update(self, time):
		self.setPos(self.getPos() + self.vel * time)
	
	def die(self):
		self.game.projectiles.remove(self)
		self.delete()
	
	def collideWithPlayer(self):
		player = self.game.player
		
		offsetDistSquared = (self.getPos() - player.getPos()).lengthSquared()
		combinedRadiusSquared = (self.radius + player.radius) ** 2
		
		if offsetDistSquared <= combinedRadiusSquared:
			player.takeDamage(self.damage)
			self.die()
	
	def collideWithEnemy(self, obj):
		obj.takeDamage(self.damage)
		self.die()
	
	def collideWithEnvironment(self):
		self.die()
	
	def terrainCollisionCheck(self):
		entries = []
		length = self.groundSphereHandler.getNumEntries()
		for i in range(length):
			entry = self.groundSphereHandler.getEntry(i)
			entries.append(entry)
		entries.sort(lambda x, y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		if (len(entries) > 0):
			for entry in entries:
				if entry.getIntoNode().getName() == "craterCollisionPlane":
					self.collideWithEnvironment()
		
		#also check the player
		self.collideWithPlayer()
	
