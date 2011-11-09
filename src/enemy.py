from unit import Unit
import random
import math

class Enemy(Unit):
	def __init__(self, models = None, anims = None, sphereString = None, game = None, xStart = 0, yStart = 0, zStart = 0):
		print sphereString
		Unit.__init__(self, models, anims, sphereString, game, xStart, yStart, zStart)
		
		self.randomMovement = 0
		self.randomMovementMax = 30 * 7
		self.minRandomVel = 200
		self.maxRandomVel = 600
		
		self.pointValue = 5
	
	def absorbMagnetism(self, field, game):
		self.changeDirectionRelative((0, field, field), game.player.getPos(), game.camera)
	
	def die(self):
		self.game.enemies.remove(self)
		Unit.die(self)
	
	def collideEnemy(self, enemy, game):
		if self.vel.length > 7 or enemy.vel.length > 7:
			self.takeDamage(self.vel.length, game)
			enemy.takeDamage(enemy.vel.length, game)
	
	def update(self, time):
		newTime = time * 1000000
		
		if math.floor(newTime % self.randomMovementMax) == 0:
			self.accel.setX(random.choice(range(-self.maxRandomVel, -self.minRandomVel) + range(self.minRandomVel, self.maxRandomVel + 1)))
			self.accel.setY(random.choice(range(-self.maxRandomVel, -self.minRandomVel) + range(self.minRandomVel, self.maxRandomVel + 1)))
		
		Unit.update(self, time)
