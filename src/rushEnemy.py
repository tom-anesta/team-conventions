from enemy import Enemy
from constants import *
from random import random

class RushEnemy(Enemy):
	def __init__(self, game, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims, "**/enemyCollisionSphere", game, xStart, yStart, zStart)
		
		self.maxSpeed = 5
		self.randomMovementMax = random.randint(30 * 7, 40 * 7)
	
	def update(self, time):
		newTime = time * 1000000
		
		if math.floor(newTime % self.randomMovementMax) == 0:
			self.rush(self.game.player)
		
		Enemy.update(self, time)
	
	def rush(self, player):
		self.applyForceFrom(-5, player.getPos())
