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
		
		#the currently active weapon
		self.currentWeapon = AREA
		
		#the maximum amount of energy available
		self.maxEnergy = 2000
		
		#the amount of energy currently available
		self.energy = self.maxEnergy
		
		#the amount of energy that is restored each second
		self.energyRegen = 1000
		
		#the energy cost of attacking with a given weapon for one second
		self.magnetCost = {NARROW:self.energyRegen + 30,
						   AREA:self.energyRegen + 50}
		
		#the strength of a sustained attack per unit of energy used
		self.magnetStrength = {NARROW:30, AREA:20}
		
		#the energy cost of a burst attack with a given weapon
		self.burstCost = {NARROW:400, AREA:600}
		
		#the strength of a burst attack with a given weapon
		#(yes, the values really do have to be this high)
		self.burstStrength = {NARROW:100000, AREA:70000}
		
		#the enemy that the narrow weapon has locked on to
		self.target = None
		
		#whether the player was attacking the previous frame; this is used
		#to determine whether to release a large burst or a smaller
		#sustained force
		self.sustainedAttack = False
		
		#action flag
		self.switchPressed = False
		
		self.extraForwardAccel = 2.2
		self.accelMultiplier *= 1.2
		self.maxTurnRate = 720
	
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
			if not self.switchPressed:
				self.switchWeapon()
				self.switchPressed = True
		else:
			self.switchPressed = False
		
		#check for attack keys
		if self.controlScheme.keyDown(PUSH) and not self.controlScheme.keyDown(PULL):
			self.attack(PUSH, game, time)
		elif self.controlScheme.keyDown(PULL) and not self.controlScheme.keyDown(PUSH):
			self.attack(PULL, game, time)
		else:
			self.sustainedAttack = False
			self.target = None
		
		#automatically regenerate energy
		self.energy += self.energyRegen * time
		self.energy = min(self.maxEnergy, self.energy)
	
	def attack(self, polarity, game, time):
		"""Selects the mode of attack and runs the appropriate attack function"""
		
		#if the player just started attacking, use a more powerful attack
		if not self.sustainedAttack:
			energyUsed = self.burstCost[self.currentWeapon]
			force = self.burstStrength[self.currentWeapon]
			
			#find a target if needed
			if self.currentWeapon == NARROW:
				self.target = game.onMouseTask()
			
			self.sustainedAttack = True
		else:
			energyUsed = self.magnetCost[self.currentWeapon] * time
			force = self.magnetStrength[self.currentWeapon] * energyUsed
		
		#if not enough energy is left, do nothing
		if energyUsed > self.energy:
			return
		
		if self.currentWeapon == NARROW:
			self.narrowAttack(polarity, game, force)
		else:
			self.areaAttack(polarity, game, force)
		
		self.energy -= energyUsed
	
	def narrowAttack(self, polarity, game, force):
		"""Performs a narrow attack on the targeted enemy (and all enemies in between and beyond?)"""
		if polarity == PULL:
			force *= -1
		
		if self.target is not None:
			distSquared = (self.position - self.target.position).lengthSquared()
			distSquared = max(130, distSquared + 50)
			
			self.target.applyForceFrom(force / distSquared, self.position)
	
	def areaAttack(self, polarity, game, force):
		"""Performs an area attack on all enemies"""
		if polarity == PULL:
			force *= -1
		
		for enemy in game.enemies:
			distSquared = (self.position - enemy.position).lengthSquared()
			distSquared = max(100, distSquared + 60)
			
			enemy.applyForceFrom(force / distSquared, self.position)
	
	def switchWeapon(self):
		"""Switch to whichever weapon is not currently being used"""
		if self.currentWeapon == NARROW:
			self.currentWeapon = AREA
		else:
			self.currentWeapon = NARROW
