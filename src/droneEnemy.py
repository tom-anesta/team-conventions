from enemy import Enemy
from unit import Unit
from constants import *

class DroneEnemy(Enemy):
	def __init__(self, game, player, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims, "**/enemyCollisionSphere", game, xStart, yStart, zStart)
		self.player = player
		
	def update(self, time):
		self.applyForceFrom(-3, self.player.getPos())
		
		Unit.update(self, time)
