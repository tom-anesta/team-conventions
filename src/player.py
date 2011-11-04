from __future__ import division

from unit import Unit
from pandac.PandaModules import Vec3
from math import cos, sin, pi, atan2
from constants import *

class Player(Unit):
	def __init__(self, controlScheme):
		models = MODELS_PATH + "SleekCraft"
		anims = {}
		Unit.__init__(self, models, anims)
		
		self.controlScheme = controlScheme
		
		self.magnetPower = 10
		self.magnetWeapon = NARROW
		self.cooldown = 0
		self.score = 0
		
		#action flags
		self.switching = False
		self.shooting = False
		
		self.extraForwardAccel = 2
		self.accelMultiplier *= 1.2
		self.maxTurnRate = 720
		
		self.shooting = False
	
	def move(self, time, camera):
		angle = self.getH()
		cameraAngle = camera.getH()
		
		#find the amount that the player wants to turn (remember, the
		#player should be 180 degrees off from the camera)
		angleOffset = (cameraAngle + 180) - angle
		while angleOffset > 180:
			angleOffset -= 360
		while angleOffset < -180:
			angleOffset += 360
		
		#turn at up to the maximum turn rate
		if angleOffset > self.maxTurnRate * time:
			angle += self.maxTurnRate * time
		elif angleOffset < -self.maxTurnRate * time:
			angle -= self.maxTurnRate * time
		else:
			angle += angleOffset * time
		self.setH(angle)
		
		#find the direction of acceleration (0 means forward, not right)
		accelX = 0
		accelY = 0
		if self.controlScheme.keyDown(LEFT):
			if not self.controlScheme.keyDown(RIGHT):
				accelX = 1
		elif self.controlScheme.keyDown(RIGHT):
			accelX = -1
		if self.controlScheme.keyDown(UP):
			if not self.controlScheme.keyDown(DOWN):
				accelY = 1
		elif self.controlScheme.keyDown(DOWN):
			accelY = -1
		
		if accelX != 0 or accelY != 0:
			#accelX and accelY swapped because of the coordinate system
			accelAngle = atan2(accelX, accelY) * 180 / pi + cameraAngle
			
			#the multiplier is determined based on how close the player is to
			#moving forward
			angleOffset = (angle + 180) - accelAngle
			while angleOffset > 180:
				angleOffset -= 360
			while angleOffset < -180:
				angleOffset += 360
			
			multiplier = max(1, self.extraForwardAccel * cos(angleOffset * pi / 180))
			
			#in this coordinate system, sin and cos need to be swapped, and
			#sin needs to be inverted
			self.applyForce(Vec3(-multiplier * sin(accelAngle * pi / 180),
								 multiplier * cos(accelAngle * pi / 180), 0))
		
		Unit.move(self, time)
	
	def detectActions(self):
		if self.controlScheme.keyDown(SWITCH):
			if not self.switching:
				self.switchWeapon()
				self.switching = True
		else:
			self.switching = False
			
		if self.controlScheme.keyDown(PUSH) and not self.controlScheme.keyDown(PULL):
			self.attack(PUSH)
		if self.controlScheme.keyDown(PULL) and not self.controlScheme.keyDown(PUSH):
			self.attack(PULL)
	
	def attack(self, action):
		if self.magnetWeapon == NARROW:
			self.narrowAttack(action)
		if self.magnetWeapon == AREA:
			self.areaAttack(action)
	
	def narrowAttack(self, action):
		print "narrow attack", action
	
	def areaAttack(self, action):
		print "area attack", action
	
	def switchWeapon(self):
		if self.magnetWeapon==NARROW:
			self.magnetWeapon = AREA
			print "switch to area"
		elif self.magnetWeapon==AREA:
			self.magnetWeapon = NARROW
			print "switch to narrow"
