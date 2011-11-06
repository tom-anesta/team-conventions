from constants import *
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
import math

class Unit(Actor):
	gravity = 20
	
	def __init__(self, models = None, anims = None):
		Actor.__init__(self, models, anims)
		
		self.health = 10
		
		self.position = Point3()
		self.vel = Vec3()
		self.accel = Vec3(0, 0, -Unit.gravity)
		
		#can be thought of as the inverse of the unit's mass
		self.accelMultiplier = 45
		self.friction = 1.7
	
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
	
	def move(self, time):
		self.vel += self.accel * time
		self.accel.set(0, 0, -Unit.gravity)
		
		self.vel -= self.vel * (self.friction * time)
		
		self.position += self.vel * time
		self.position.setZ(max(0, self.position.getZ()))
		
		self.setPos(self.position.getX(), self.position.getY(), self.position.getZ())
