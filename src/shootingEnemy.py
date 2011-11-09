from enemy import Enemy
from bullet import Bullet
import math

from pandac.PandaModules import Point3

class ShootingEnemy(Enemy):
	def __init__(self, game, xStart = 0, yStart = 0, zStart = 0):
		models = MODELS_PATH + "HovercraftOne"
		anims = None
		Enemy.__init__(self, models, anims, "**/enemyCollisionSphere", game, xStart, yStart, zStart)
		self.cooldownLength = 5
		self.cooldownleft = self.cooldownLength
		self.preferedDistanceFromPlayer = 15
	
	def shoot(self, player):
		self.game.projectiles.append(Bullet(self.game, game.render, player.getPos() - self.getPos()))
		
	def update(self, time):
		player = self.game.player
		
		angle = math.atan2(self.getY() - player.getY(), \
							self.getX() - player.getX())
		angle += math.pi/8
		
		targetPoint = Point3(player.getX() + self.preferedDistanceFromPlayer * math.cos(angle), \
							player.getY() + self.preferedDistanceFromPlayer * math.sin(angle), self.getZ())
		self.applyForceFrom(-2, targetPoint)
		
		Enemy.update(self, time)
		
		angle = math.atan2(player.getY() - self.getY(), \
							player.getX() - self.getX())
		self.setH(angle * 180 / math.pi)
		
		self.cooldownLeft -= time
		if self.cooldownLeft <= 0:
			self.cooldownLeft = self.cooldownLength
			self.shoot(player)