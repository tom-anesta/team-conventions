from __future__ import division

from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionSphere
from pandac.PandaModules import CollisionHandlerEvent

#from pandac.PandaModules import CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import CollisionHandlerPusher
from pandac.PandaModules import BitMask32
import math

class Unit(Actor):
	gravity = 20
	speedThreshold = 15
	units = []
	
	def __init__(self, models = None, anims = None, sphereString = "**/CollisionSphere", game = None, xStart = 0, yStart = 0, zStart = 0, radius = 3):
		Actor.__init__(self, models, anims)
		
		self.game = game
		
		self.health = 10
		self.heightOffset = 3
		
		#set up the position
		self.setPos(xStart, yStart, zStart)
		self.prevPosition = self.getPos()
		#self.lastPosition = Point3()
		self.vel = Vec3()
		self.accel = Vec3(0, 0, -Unit.gravity)
		#define the position that will be treated as the center of the map
		self.wCenter = Point3(0, 0, 0)
		
		#register this unit
		#Unit.units.append(self)
		
		#the radius of the sphere around this
		self.radius = 3.5
		
		#determines how easily this unit
		self.mass = 10
		
		#the damage this deals to other units upon collision when the 
		self.collisionAttackPower = 1
		
		#set up Panda's collision handling
		#self.collisionNodePath = self.attachNewNode(CollisionNode('cNode'))
		#self.collisionNodePath.node().addSolid(CollisionSphere(0, 0, 0, radius))
		#first the pusher
		'''
		self.collisionNodePath = self.find(sphereString)
		if self.collisionNodePath.isEmpty():
			self.collisionNodePath = self.find("**/enemyCollisionSphere")
		self.collisionNodePath.node().setFromCollideMask(BitMask32.bit(0))
		self.collisionNodePath.node().setIntoCollideMask(BitMask32.bit(0))
		
		#build our collision pusher
		self.collisionHandler = CollisionHandlerPusher()
		self.collisionHandler.addCollider(self.collisionNodePath, self)
		'''
		
		
		cSphere = CollisionSphere((0,0,1), 2)
		cNode = CollisionNode("panda")
		cNode.addSolid(cSphere)
		cNode.setIntoCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
		cNode.setFromCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
		self.collisionNodePath = self.attachNewNode(cNode)
		self.collisionNodePath.show()
		#registers a from object with the traverser with a corresponding handler
		
		#set pattern for event sent on collision
		# "%in" is substituted with the name of the into object
		self.collisionHandler = CollisionHandlerEvent()
		self.collisionHandler.setInPattern("impacted-%in")
		game.cTrav.addCollider(self.collisionNodePath, self.collisionHandler)
		
		
		
		
		#check for colllisions with the ground
		self.groundRay = CollisionRay()
		self.groundRay.setOrigin(0, 0, 4000)
		self.groundRay.setDirection(0, 0, -1)
		self.groundCol = CollisionNode('unitRay')
		self.groundCol.addSolid(self.groundRay)
		self.groundCol.setFromCollideMask(BitMask32(TERRAIN_RAY_MASK))
		self.groundCol.setIntoCollideMask(BitMask32.allOff())
		self.groundColNode = self.attachNewNode(self.groundCol)
		self.groundHandler = CollisionHandlerQueue()
		game.cTrav.addCollider(self.groundColNode, self.groundHandler)
		
		#can be thought of as the inverse of the unit's mass
		self.accelMultiplier = 45
		self.friction = 1.7
		self.disableFriction = False
		
		self.nodePath = None
		self.shootable = True
	
	def registerCollider(self, collisionTraverser):#this may be deprecated by the use of putting the collision registering in init
		#collisionTraverser.addCollider(self.collisionNodePath, self.collisionHandler)
		pass
	
	def applyForceFrom(self, magnitude, sourcePosition):
		forceVector = self.getPos() - sourcePosition
		forceVector.normalize()
		forceVector *= magnitude
		
		self.applyForce(forceVector)
	
	def applyForce(self, forceVector):
		self.accel += forceVector * self.accelMultiplier
	
	def applyConstantVelocityFrom(self, magnitude, sourcePosition):
		velVector = self.getPos() - sourcePosition
		velVector.normalize()
		velVector *= magnitude
		
		self.applyConstantVelocity(velVector)
	
	def applyConstantVelocity(self, velVector):
		self.vel = velVector

	def takeDamage(self, num):
		self.health -= num
		
		if self.health <= 0:
			self.die()
	
	def die(self):
		Unit.units.remove(self)
		self.delete()
	
	def turn(self, magnitude):
		pass
	
	def update(self, time):
		self.vel += self.accel * time
		self.accel.set(0, 0, -Unit.gravity)
		
		if not self.disableFriction:
			self.vel -= self.vel * (self.friction * time)
		
		self.prevPosition = self.getPos()
		
		self.setPos(self.getPos() + self.vel * time)
		self.setZ(max(-100, self.getZ()))
		
		self.checkCollisions(time)
	
	def checkCollisions(self, time):
		for otherUnit in Unit.units:
			if otherUnit != self:
				offsetVector = self.getPos() - otherUnit.getPos()
				offsetDistSquared = offsetVector.lengthSquared()
				combinedRadiusSquared = (self.radius + otherUnit.radius) ** 2
				
				if offsetDistSquared <= combinedRadiusSquared:
					invTotalMass = 1 / (self.mass + otherUnit.mass)
					
					offsetVector.normalize()
					offsetVector *= self.radius + otherUnit.radius
					
					centerOfMass = (self.getPos() * self.mass + otherUnit.getPos() * otherUnit.mass) \
									* invTotalMass
					
					selfOffset = offsetVector * (self.mass * invTotalMass)
					otherOffset = offsetVector * (-otherUnit.mass * invTotalMass)
					
					self.setPos(centerOfMass + selfOffset)
					otherUnit.setPos(centerOfMass + otherOffset)
					
					if time != 0:
						self.vel = (self.getPos() - self.prevPosition) * (1 / time)
						otherUnit.vel = (otherUnit.getPos() - otherUnit.prevPosition) * (1 / time)
	
	def terrainCollisionCheck(self):
		entries = []
		length = self.groundHandler.getNumEntries()
		for i in range(length):
			entry = self.groundHandler.getEntry(i)
			entries.append(entry)
		entries.sort(lambda x, y: cmp(y.getSurfacePoint(render).getZ(), x.getSurfacePoint(render).getZ()))
		if (len(entries) > 0):
			for entry in entries:
				if entry.getIntoNode().getName() == "craterCollisionPlane":
					zVal = entry.getSurfacePoint(render).getZ()
					if zVal >= MAX_HEIGHT:#apply a force toward the center
						self.applyForce(self.wCenter - Point3((self.getX() * GROUND_REPULSION_MULTIPLIER), (self.getY() * GROUND_REPULSION_MULTIPLIER), 0))
						'''
						this is a little bit hackish, what is done is that a force in the x and y direction is created proportional to your distance from the origin.  this will only 
						work effectively if the crater is xy centered in the environment
						'''
					else:
						self.setZ(max(zVal, self.getZ()))
					break
				
				
			