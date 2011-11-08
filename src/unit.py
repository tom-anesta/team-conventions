from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionSphere
from pandac.PandaModules import CollisionHandlerPusher
import math

class Unit(Actor):
	gravity = 20
	
	def __init__(self, models = None, anims = None, xStart=0, yStart=0, zStart=0, radius = 3):
		Actor.__init__(self, models, anims)
		
		self.health = 10
		
		self.position = Point3(xStart, yStart, zStart)
		#self.lastPosition = Point3()
		self.vel = Vec3()
		self.accel = Vec3(0, 0, -Unit.gravity)
		
		#set up the collision handling
#		self.collisionNodePath = self.attachNewNode(CollisionNode('cNode'))
#		self.collisionNodePath.node().addSolid(CollisionSphere(0, 0, 0, radius))
#		self.collisionNodePath.show()
#		
#		self.collisionHandler = CollisionHandlerPusher()
#		self.collisionHandler.addCollider(self.collisionNodePath, self)
		
		#can be thought of as the inverse of the unit's mass
		self.accelMultiplier = 45
		self.friction = 1.7
		
		self.nodePath = None
		self.shootable = True
	
	def registerCollider(self, collisionTraverser):
		pass
#		collisionTraverser.addCollider(self.collisionNodePath, self.collisionHandler)
	
	def applyForceFrom(self, magnitude, sourcePosition):
		forceVector = self.position - sourcePosition
		forceVector.normalize()
		forceVector *= magnitude
		
		self.applyForce(forceVector)
	
	def applyForce(self, forceVector):
		self.accel += forceVector * self.accelMultiplier

	def takeDamage(self, num):
		self.health -= num
	
	def collideObstacle(self):
		if (self.vel.length > 7):
			self.takeDamage(self.vel.length)
	
	def turn(self, magnitude):
		pass
	
	def update(self, time):
		self.vel += self.accel * time
		self.accel.set(0, 0, -Unit.gravity)
		
		self.vel -= self.vel * (self.friction * time)
		
		self.position += self.vel * time
		self.position.setZ(max(-100, self.position.getZ()))
		
		Actor.setPos(self, self.position.getX(), self.position.getY(), self.position.getZ())
	
	def setPos(self, x, y, z):
		self.position.set(x, y, z)
		Actor.setPos(self, x, y, z)
	
	def setX(self, x):
		self.position.setX(x)
		Actor.setX(self, x)
	
	def setY(self, y):
		self.position.setY(y)
		Actor.setY(self, y)
	
	def setZ(self, z):
		self.position.setX(z)
		Actor.setZ(self, z)
