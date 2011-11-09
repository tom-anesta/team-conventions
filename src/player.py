from __future__ import division

from unit import Unit
from pandac.PandaModules import Vec3
from math import cos, sin, pi, atan2
from constants import *
from panda3d.core import CollisionHandlerQueue

from pandac.PandaModules import Spotlight
from pandac.PandaModules import VBase4
from pandac.PandaModules import PerspectiveLens

class Player(Unit):
	def __init__(self, controlScheme, camera, game, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "SleekCraft"
		anims = {}
		Unit.__init__(self, models, anims, "**/CollisionSphere", game, xStart, yStart, zStart)
		
		self.controlScheme = controlScheme
		self.camera = camera
		self.game = game
		
		#set up sounds
		self.thrustSound = game.loader.loadSfx(SFX_PATH + "thrust.wav")
		self.electricSound = game.loader.loadSfx(SFX_PATH + "electricity.wav")
		self.magnetSound = game.loader.loadSfx(SFX_PATH + "magnet.wav")
		
		#set up the collisions in unit
		
		#set up the headlamp specific to the model
		headLampMain = Spotlight('headLampMain')
		#headLampMain.showFrustum()
		headLampMain.setColor(VBase4(1, 1, 1, 1))
		mlens = PerspectiveLens()
		mlens.setNearFar(0.25, 1500)
		headLampMain.setLens(mlens)
		headLampMainnode = self.attachNewNode(headLampMain)
		headLampMainnode.setPos(self.find("**/LightCubeMain").getPos())
		headLampMainnode.setHpr(-180, 0, 0)#reverse completely because our model is backwards
		game.render.setLight(headLampMainnode)
		
		headLampLeft = Spotlight('headLampLeft')
		#headLampLeft.showFrustum()
		headLampLeft.setColor(VBase4(0.6, 0.6, 0.6, 1))
		llens = PerspectiveLens()
		headLampLeft.setLens(llens)
		llens.setNearFar(0.25, 500)
		headLampLeftnode = self.attachNewNode(headLampLeft)
		headLampLeftnode.setPos(self.find("**/LightCubeLeft").getPos())
		headLampLeftnode.setHpr(-105, 0, 0)#reverse completely because our model is backwards
		game.render.setLight(headLampLeftnode)
		
		headLampRight = Spotlight('headLampRight')
		#headLampRight.showFrustum()
		headLampRight.setColor(VBase4(0.6, 0.6, 0.6, 1))
		rlens = PerspectiveLens()
		rlens.setNearFar(0.25, 500)
		headLampRight.setLens(rlens)
		headLampRightnode = self.attachNewNode(headLampRight)
		headLampRightnode.setPos(self.find("**/LightCubeRight").getPos())
		headLampRightnode.setHpr(105, 0, 0)#reverse completely because our model is backwards
		game.render.setLight(headLampRightnode)
		
		self.health = 100
		self.collisionAttackPower = 0
		
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
		self.magnetStrength = {NARROW:1, AREA:20}
		
		#the energy cost of a burst attack with a given weapon
		self.burstCost = {NARROW:0, AREA:600}
		
		#the strength of a burst attack with a given weapon
		#(yes, the area value really does have to be this high)
		self.burstStrength = {NARROW:90, AREA:7000}
		
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
		
		#self.shooting = False
		
		#used in main to check if the unit can be shot with the narrow attack
		self.shootable = False
	
	def move(self, time):
		angle = self.getH()
		cameraAngle = self.camera.getH()
		
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
		
		soundcheck = False#necessary due to the structure of our if else statements
		#we are currently experiencing technical difficulties with this check.  please wait while we attempt to restore the quality of your audio experience
		if self.controlScheme.keyDown(LEFT):
			if not self.controlScheme.keyDown(RIGHT):
				#print "left is down"
				accelX = 1
				self.thrustSound.setLoop(True)
				if self.thrustSound.status() is not self.thrustSound.PLAYING:
					#print "test left"
					self.thrustSound.play()
					soundcheck = True
					#print "value after left is " + str(soundcheck)
		elif self.controlScheme.keyDown(RIGHT):
			#print "right is down"
			accelX = -1
			self.thrustSound.setLoop(True)
			if self.thrustSound.status() is not self.thrustSound.PLAYING:
				#print "test right"
				self.thrustSound.play()
				soundcheck = True
				#print "value after right is " + str(soundcheck)
		if self.controlScheme.keyDown(UP):
			if not self.controlScheme.keyDown(DOWN):
				#print "up is down"
				accelY = 1
				self.thrustSound.setLoop(True)
				if self.thrustSound.status() is not self.thrustSound.PLAYING:
					self.thrustSound.play()
				else:
					pass
		elif self.controlScheme.keyDown(DOWN):
			#print "down is down"
			accelY = -1
			self.thrustSound.setLoop(True)
			if self.thrustSound.status() is not self.thrustSound.PLAYING:
				self.thrustSound.play()
		else:
			#print soundcheck#for some reason we miss left or right key down events every second frame, this is causing sound to reset for left and right every second frame.  not sure what to do
			if self.thrustSound.status() == self.thrustSound.PLAYING and not soundcheck:
				#print "check"
				self.thrustSound.stop()
		
		#then soundcheck goes out of scope
		
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
	
	def update(self, time):
		"""Run all major player operations each frame"""
		#check for weapon switch key
		if self.controlScheme.keyDown(SWITCH):
			if not self.switchPressed:
				self.switchWeapon()
				self.switchPressed = True
		else:
			self.switchPressed = False
		
		self.targetEnemy()
		
		#check for attack keys
		if self.controlScheme.keyDown(PUSH) and not self.controlScheme.keyDown(PULL):
			self.attack(PUSH, time)
			#include sound
			#self.electricSound.play()
			if self.electricSound.status() is not self.electricSound.PLAYING:
				#self.electricSound.setTime(self.electricSound.getTime())#reset to the current time and play it from there
				self.electricSound.play()
		elif self.controlScheme.keyDown(PULL) and not self.controlScheme.keyDown(PUSH):
			self.attack(PULL, time)
			#include sound
			#self.magnetSound.setLoop(True)
			if self.magnetSound.status() is not self.magnetSound.PLAYING:
				#self.magnetSound.setTime(self.magnetSound.getTime())
				self.magnetSound.play()
				
		else:
			self.sustainedAttack = False
			#self.target = None
			if self.electricSound.status() == self.electricSound.PLAYING:
				#self.electricSound.setTime(float(0))#for some reason this is not resetting the time
				#print self.electricSound.getTime()
				self.electricSound.stop()
			if self.magnetSound.status() == self.magnetSound.PLAYING:
				#self.magnetSound.setTime(float(0))#for some reason this is not resetting the time
				#print self.magnetSound.getTime()
				self.magnetSound.stop()
				
		#i am of the opinion that sound is somehow completely borked here
		
		#automatically regenerate energy
		self.energy += self.energyRegen * time
		self.energy = min(self.maxEnergy, self.energy)
		
		self.move(time)
		Unit.update(self, time)
	
	def collideWithObject(self, obj):
		Unit.collideWithObject(obj)
	
	def targetEnemy(self):
		"""Either selects a new targeted enemy or wipes the current one, depending on player action"""
		if self.currentWeapon == AREA or (not self.controlScheme.keyDown(PUSH) and not self.controlScheme.keyDown(PULL)):
			self.target = None
		elif self.currentWeapon == NARROW and (self.controlScheme.keyDown(PUSH) or self.controlScheme.keyDown(PULL)):
			self.target = self.game.selectTarget()
	
	def attack(self, polarity, time):
		"""Selects the mode of attack and runs the appropriate attack function"""
		
		#if the player just started attacking, use a more powerful attack
		if not self.sustainedAttack:
			energyUsed = self.burstCost[self.currentWeapon]
			force = self.burstStrength[self.currentWeapon]
			
			self.sustainedAttack = True
		else:
			energyUsed = self.magnetCost[self.currentWeapon] * time
			force = self.magnetStrength[self.currentWeapon] * energyUsed
		
		#if not enough energy is left, do nothing
		if energyUsed > self.energy:
			return
		
		if self.currentWeapon == NARROW:
			self.narrowAttack(polarity, force)
		else:
			self.areaAttack(polarity, force)
		
		self.energy -= energyUsed
	
	def narrowAttack(self, polarity, force):
		"""Performs a narrow attack on the targeted enemy"""
		
		if polarity == PULL:
			force *= -1
		
		if self.target is not None:
			if polarity == PULL:
				self.target.applyConstantVelocityFrom(force, self.getPos())
			elif polarity == PUSH:
				self.target.applyForceFrom(force, self.getPos())
			
	
	def areaAttack(self, polarity, force):
		"""Performs an area attack on all enemies"""
		if polarity == PULL:
			force *= -1
		
		for enemy in self.game.enemies:
			distSquared = (self.getPos() - enemy.getPos()).lengthSquared()
			if polarity == PULL:
				distSquared = max(450, distSquared) / 2
			else:
				distSquared = max(350, distSquared) / 2
			
			enemy.applyForceFrom(force / distSquared, self.getPos())
	
	def switchWeapon(self):
		"""Switch to whichever weapon is not currently being used"""
		if self.currentWeapon == NARROW:
			self.currentWeapon = AREA
		else:
			self.currentWeapon = NARROW
