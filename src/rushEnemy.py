from enemy import Enemy
from constants import *

class RushEnemy(Enemy):
	def __init__(self):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims)
		
		self.maxSpeed = 5
	
	def rush(self, player):
		self.applyForceFrom(-3, player.position)
