from unit import Unit
import random
import math
from constants import *

class Enemy(Unit):
	def __init__(self, models = None, anims = None, sphereString = None, game = None, xStart = 0, yStart = 0, zStart = 0):
		Unit.__init__(self, models, anims, sphereString, game, xStart, yStart, zStart)
		
		#set up sounds
		self.deathSound = game.loader.loadSfx(SFX_PATH + "enemy_death.wav")
		
		self.randomMovement = 0
		self.randomMovementMax = 30 * 7
		self.minRandomVel = 1000
		self.maxRandomVel = 2000
	
	def die(self, game):
		self.deathSound.play()
		self.game.enemies.remove(self)
		Unit.die(self)
	
	def takeDamage(self, num):
		Unit.takeDamage(num)
		if self.health <= 0:
			self.die(game)
	
	def collideEnemy(self, enemy, game):
		if self.vel.length > 7 or enemy.vel.length > 7:
			self.takeDamage(self.vel.length, game)
			enemy.takeDamage(enemy.vel.length, game)
	
	def update(self, time):
		Unit.update(self, time)
