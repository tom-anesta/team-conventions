from unit import Unit
import random

class Enemy(Unit):
	def __init__(self, models = None, anims = None):
		Unit.__init__(self, models, anims)
		
		self.randomMovement = 0
		self.randomMovementMax = 30*2
		self.minRandomVel = -5
		self.maxRandomVel = 5
	
	def absorbMagnetism(self, field, game):
		self.changeDirectionRelative((0,field,field), game.player.position, game.camera)
	
	def die(self, game):
		game.enemies.remove(self)
	
	def takeDamage(self, num, game):
		Unit.takeDamage(num)
		if self.health <= 0:
			self.die(game)
	
	def collideEnemy(self, enemy, game):
		if self.vel.length > 7 or enemy.vel.length > 7:
			self.takeDamage(self.vel.length, game)
			enemy.takeDamage(enemy.vel.length, game)
	
	def move(self, time):
		if time % self.randomMovementMax == 0:
			self.vel.setX(random.randint(self.minRandomVel, self.maxRandomVel))
			self.vel.setY(random.randint(self.minRandomVel, self.maxRandomVel))
		
		Unit.move(self, time)