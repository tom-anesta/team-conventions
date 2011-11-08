from enemy import Enemy
from constants import *

class RushEnemy(Enemy):
	def __init__(self, game, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims, "**/enemyCollisionSphere", game, xStart, yStart, zStart)
		
		self.maxSpeed = 5
	
	def rush(self, player):
		self.applyForceFrom(-3, player.getPos())
