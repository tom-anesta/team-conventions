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
	def __init__(self, models = None, anims = None, sphereString="**/bulletCollisionSphere", game = None, parent = None, pos = Point3(), vel = Vec3()):
		Actor.__init__(self, models, anims)
		
		self.game = game
		
		self.damage = 10
		self.parent = parent
		
		#self.position = Point3(xStart, yStart, zStart)
		self.setPos(pos.getX(), pos.getY(), pos.getZ())
		self.vel = vel
		
		self.collisionNodePath = self.find(sphereString)
		if self.collisionNodePath.isEmpty():
			self.collisionNodePath = self.find("**/enemyCollisionSphere")
		if self.collisionNodePath.isEmpty():
			print "aaaaaaa"
		else:
			print "okay"
		self.collisionNodePath.node().setFromCollideMask(BitMask32.bit(0))
		self.collisionNodePath.node().setIntoCollideMask(BitMask32.bit(0))
		
		self.groundSphereHandler = CollisionHandlerQueue()
		self.game.cTrav.addCollider(self.collisionNodePath, self.groundSphereHandler)
		
		self.collisionHandler = CollisionHandlerPusher()
		self.collisionHandler.addCollider(self.collisionNodePath, self)
	
	def registerCollider(self, collisionTraverser):
		collisionTraverser.addCollider(self.collisionNodePath, self.collisionHandler)
		pass
	
	def applyConstantVelocityFrom(self, magnitude, sourcePosition):
		velVector = self.getPos() - sourcePosition
		velVector.normalize()
		velVector *= magnitude
		
		self.applyConstantVelocity(velVector)
	
	def applyConstantVelocity(self, velVector):
		self.vel = velVector
	
	def collideObstacle(self):
		if (self.vel.length > 7):
			self.takeDamage(self.vel.length)
	
	def turn(self, magnitude):
		pass
	
	def update(self, time):
		position = self.getPos()
		position += self.vel * time
		position.setZ(max(-100, position.getZ()))
		
		self.setPos(position.getX(), position.getY(), position.getZ())
	
	def die(self):
		self.projectiles.remove(self)
	
	def collideWithPlayer(self, obj):
		print type(obj)
		self.die()
	
	def collideWithEnemy(self, obj):
		print type(obj)
		self.die()
	
	def collideWithEnvironment(self):
		print "environment"
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
				
				elif entry.getIntoNode().getName() == "enemyCollisionSphere":
					name =  entry.getIntoNodePath().getParent().getParent().getParent().getName()
					
					if name == "render" or name == self.parent.getName():
						continue
					
					self.collideWithEnemy(self.game.actors[name])
				
				elif entry.getIntoNode().getName() == "playerCollisionSphere":
					name =  entry.getIntoNodePath().getParent().getParent().getParent().getName()
					
					if name == "render" or name == self.parent.getName():
						continue
					
					self.collideWithEnemy(self.game.actors[name])
	
