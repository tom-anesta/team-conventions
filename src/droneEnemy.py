from enemy import Enemy

class droneEnemy(Enemy):
	def __init__(self):
		models = None
		anims = None
		Enemy.__init__(self, models, anims)
	
		self.pointValue = 1
		
	def update(self, time):
		self.applyForceFrom(-0.1, self.player.getPos())
		
		Unit.update(self, time)
