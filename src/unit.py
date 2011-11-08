from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionSphere
<<<<<<< HEAD
#from pandac.PandaModules import CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue
=======
from pandac.PandaModules import CollisionHandlerPusher
from pandac.PandaModules import BitMask32
>>>>>>> 776e577854f5b402a603a5341e925c53b0463106
import math

class Unit(Actor):
	gravity = 20
	
<<<<<<< HEAD
	
	
	def __init__(self, models = None, anims = None, sphereString="**/CollisionSphere", game = None, xStart=0, yStart=0, zStart=0, radius = 3):
=======
	def __init__(self, models = None, anims = None, xStart = 0, yStart = 0, zStart = 0, radius = 3):
>>>>>>> 776e577854f5b402a603a5341e925c53b0463106
		Actor.__init__(self, models, anims)
		
		self.health = 10
		self.heightOffset = 3
		
<<<<<<< HEAD
		#self.position = Point3(xStart, yStart, zStart)
		self.setPos(xStart, yStart, zStart)
=======
>>>>>>> 776e577854f5b402a603a5341e925c53b0463106
		#self.lastPosition = Point3()
		self.vel = Vec3()
		self.accel = Vec3(0, 0, -Unit.gravity)
		
		'''
		#set up the collision handling
<<<<<<< HEAD
#		self.collisionNodePath = self.attachNewNode(CollisionNode('cNode'))
#		self.collisionNodePath.node().addSolid(CollisionSphere(0, 0, 0, radius))
#		self.collisionNodePath.show()
#		
#		self.collisionHandler = CollisionHandlerPusher()
#		self.collisionHandler.addCollider(self.collisionNodePath, self)
		'''
		
		#set up collision handling
		self.groundSphereCol = self.find("**/CollisionSphere")
		if self.groundSphereCol.isEmpty():
			print "playerGroundCol is empty"
		#self.playerGroundCol.setCollisionMask(BitMask32(0x00))
		self.registerCollider(game.cTrav)
		#self.playerGroundCol.setFromCollideMask(BitMask32.bit(0))
		#self.playerGroundCol.setIntoCollideMask(BitMask32.allOff())
		self.groundSphereHandler = CollisionHandlerQueue()
		game.cTrav.addCollider(self.groundSphereCol, self.groundSphereHandler)
		
=======
		#self.collisionNodePath = self.attachNewNode(CollisionNode('cNode'))
		#self.collisionNodePath.node().addSolid(CollisionSphere(0, 0, 0, radius))
		self.collisionNodePath = self.find("**/enemyCollisionSphere")
		if self.collisionNodePath.isEmpty():
			self.collisionNodePath = self.find("**/CollisionSphere")
		self.collisionNodePath.node().setFromCollideMask(BitMask32.bit(0))
		self.collisionNodePath.node().setIntoCollideMask(BitMask32.bit(0))
		
		self.collisionHandler = CollisionHandlerPusher()
		self.collisionHandler.addCollider(self.collisionNodePath, self)
>>>>>>> 776e577854f5b402a603a5341e925c53b0463106
		
		#can be thought of as the inverse of the unit's mass
		self.accelMultiplier = 45
		self.friction = 1.7
		
		self.nodePath = None
		self.shootable = True
	
	def registerCollider(self, collisionTraverser):
		collisionTraverser.addCollider(self.collisionNodePath, self.collisionHandler)
		pass
	
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
		
		position = self.getPos()
		position += self.vel * time
		position.setZ(max(-100, position.getZ()))
		
<<<<<<< HEAD
		Actor.setPos(self, self.position.getX(), self.position.getY(), self.position.getZ())
	
	def setPos(self, x, y, z):
		#self.position.set(x, y, z)
		Actor.setPos(self, x, y, z)
	
	def setX(self, x):
		#self.position.setX(x)
		Actor.setX(self, x)
	
	def setY(self, y):
		#self.position.setY(y)
		Actor.setY(self, y)
	
	def setZ(self, z):
		#self.position.setX(z)
		Actor.setZ(self, z)
=======
		self.setPos(position.getX(), position.getY(), position.getZ())
>>>>>>> 776e577854f5b402a603a5341e925c53b0463106
