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
		
		self.magnetPower = 300
		self.magnetWeapon = AREA
		self.magnetBar = 1000
		self.magnetBarMax = 1000
		self.magnetCost = {NARROW:16, AREA:32}
		self.magnetRegen = 2500
		self.cooldown = 0
		self.score = 0
		
		self.target = None
		
		#action flags
		self.switching = False
		self.shooting = False
		
		self.extraForwardAccel = 2.2
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
	
	def update(self, game, time):
		"""Run all major player operations each frame"""
		#check for weapon switch key
		if self.controlScheme.keyDown(SWITCH):
			if not self.switching:
				self.switchWeapon()
				self.switching = True
		else:
			self.switching = False
		
		#check for attack keys
		if self.magnetBar > 0 and self.controlScheme.keyDown(PUSH) and not self.controlScheme.keyDown(PULL):
			self.attack(PUSH, game)
		if self.magnetBar > 0 and self.controlScheme.keyDown(PULL) and not self.controlScheme.keyDown(PUSH):
			self.attack(PULL, game)
		
		#automatically regenerate the magnet bar's power
		self.magnetBar += self.magnetRegen * time
	
	def decrementMagnetBar(self):
		"""Subtract from the magnet bar by the amount specified in __init__"""
		self.magnetBar -= self.magnetCost[self.magnetWeapon]
	
	def attack(self, polarity, game):
		"""Selects the mode of attack and runs the appropriate attack function"""
		
		#if magnet is set to narrow and magnet bar has enough power to perform a narrow attack
		if self.magnetWeapon == NARROW and self.magnetBar >= self.magnetCost[NARROW]:
			self.narrowAttack(polarity, game)
		
		#if magnet is set to area and magnet bar has enough power to perform an area attack
		if self.magnetWeapon == AREA and self.magnetBar >= self.magnetCost[AREA]:
			self.areaAttack(polarity, game)
	
	def narrowAttack(self, polarity, game):
		"""Performs a narrow attack on the targeted enemy (and all enemies in between and beyond?)"""
		
		#decide on direction of force based on polarity
		direction = -1 if polarity==PUSH else 1
		
		if self.target is not None:
			self.target.applyForceFrom((direction*self.magnetPower)*(1.5), self.position)
		
		self.decrementMagnetBar()
	
	def areaAttack(self, polarity, game):
		"""Performs an area attack on all enemies"""
		
		#decide on direction of force based on polarity
		if polarity == PUSH:
			force = -self.magnetPower
		else:
			force = self.magnetPower
		
		#apply force to all enemies
		for enemy in game.enemies:
			distSquared = (self.position - enemy.position).lengthSquared()
			if polarity == PULL:
				distSquared = max(130, distSquared)
			else:
				distSquared = max(80, distSquared)
			
			enemy.applyForceFrom(force / distSquared, self.position)
		
		self.decrementMagnetBar()
	
	def switchWeapon(self):
		"""Switch to whichever weapon is not currently being used"""
		if self.magnetWeapon == NARROW:
			self.magnetWeapon = AREA
		elif self.magnetWeapon == AREA:
			self.magnetWeapon = NARROW
