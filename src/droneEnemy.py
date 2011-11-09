from enemy import Enemy
from constants import *
from unit import Unit

class DroneEnemy(Enemy):
	def __init__(self, game, player, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims, "**/enemyCollisionSphere", game, xStart, yStart, zStart)
	
		self.pointValue = 1
		self.player = player
		
	def update(self, time):
		self.applyForceFrom(-0.1, self.player.getPos())
		
		Unit.update(self, time)
