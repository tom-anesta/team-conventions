from unit import Unit
import random
import math

class Enemy(Unit):
	def __init__(self, models = None, anims = None):
		Unit.__init__(self, models, anims)
		
		self.randomMovement = 0
		self.randomMovementMax = 30*7
		self.minRandomVel = 1000
		self.maxRandomVel = 2000
	
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
		newTime = time*1000000
		
		print math.floor(newTime % self.randomMovementMax)
		
		if math.floor(newTime % self.randomMovementMax) == 0:
			self.accel.setX(random.choice(range(-self.maxRandomVel, -self.minRandomVel)+range(self.minRandomVel, self.maxRandomVel+1)))
			self.accel.setY(random.choice(range(-self.maxRandomVel, -self.minRandomVel)+range(self.minRandomVel, self.maxRandomVel+1)))
		
		Unit.move(self, time)