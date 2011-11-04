from enemy import Enemy

class droneEnemy(Enemy):
	def __init__(self):
		models = None
		anims = None
		Enemy.__init__(self, models, anims)
		
		self.maxSpeed = 5