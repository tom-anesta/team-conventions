from enemy import Enemy

class electricEnemy(Enemy):
	def __init__(self):
		models = None
		anims = None
		Enemy.__init__(self, models, anims)
	
	def shoot(self, player):
		pass