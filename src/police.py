from enemy import Enemy

class police(Enemy):
	def __init__(self):
		models = None
		anims = None
		Enemy.__init__(self, models, anims)