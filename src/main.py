from __future__ import division
from sys import exit

from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import KeyboardButton
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import DirectionalLight
from pandac.PandaModules import AmbientLight
from pandac.PandaModules import PointLight
from pandac.PandaModules import Vec4

from math import pi, sin, cos, sqrt, pow, atan2
from unit import Unit
from player import Player
from rushEnemy import RushEnemy
from constants import *
from controlScheme import ControlScheme

class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		#get window properties
		self.winProps = WindowProperties()
		self.winProps.setFullscreen(True)
		self.winProps.setCursorHidden(True)
		base.win.requestProperties(self.winProps)
		
		self.winProps = base.win.getProperties()
		self.screenHeight = self.winProps.getYSize()
		
		#set up the control scheme
		self.controlScheme = ControlScheme(base.mouseWatcherNode, base.win, \
										[LEFT, RIGHT, UP, DOWN, PAUSE, PULL, PUSH, SWITCH, QUIT])
		
		#disable the automatic task to move the camera
		#(this does not actually disable the mouse)
		base.disableMouse()
		
		#object lists
		self.enemies = []
		self.obstacles = []
		
		#not paused by default
		self.paused = False
		self.pauseWasPressed = False
		
		#variables for tracking time
		self.previousFrameTime = 0
		
		#load and render the environment model
		self.environment = self.loader.loadModel("models/environment")
		self.environment.reparentTo(self.render)
		self.environment.setScale(0.25, 0.25, 0.25)
		self.environment.setPos(-8, 42, 0)
		
		#place the player in the environment
		self.player = Player(self.controlScheme)
		self.player.setH(180)
		self.player.reparentTo(self.render)
		
		#add an enemy
		self.tempEnemy = RushEnemy()
		self.tempEnemy.setPos(-20, 0, 0)
		self.tempEnemy.reparentTo(self.render)
		
		self.tempEnemy2 = RushEnemy()
		self.tempEnemy2.setPos(40, 50, 0)
		self.tempEnemy2.reparentTo(self.render)
		
		self.tempEnemy3 = RushEnemy()
		self.tempEnemy3.setPos(20, 80, 0)
		self.tempEnemy3.reparentTo(self.render)
		
		self.enemies.append(self.tempEnemy)
		self.enemies.append(self.tempEnemy2)
		self.enemies.append(self.tempEnemy3)
		
		#add some lights
		topLight = DirectionalLight("top light")
		topLight.setColor(Vec4(0.9, 0.9, 0.6, 1))
		topLight.setDirection(Vec3(130, -60, 0))
		self.render.setLight(self.render.attachNewNode(topLight))
		horizontalLight = DirectionalLight("horizontal light")
		horizontalLight.setColor(Vec4(1, 0.9, 0.8, 1))
		horizontalLight.setDirection(Vec3(-90, 0, 0))
		self.render.setLight(self.render.attachNewNode(horizontalLight))
		ambientLight = AmbientLight("ambient light")
		ambientLight.setColor(Vec4(0.5, 0.5, 0.5, 1))
		self.render.setLight(self.render.attachNewNode(ambientLight))
		
		#the distance the camera is from the player
		self.cameraHOffset = 45
		self.cameraVOffset = 10
		
		#register the update task
		self.taskMgr.add(self.updateGameTask, "updateGameTask")
	
	def updateGameTask(self, task):
		elapsedTime = task.time - self.previousFrameTime
		self.previousFrameTime = task.time
		
		if self.controlScheme.keyDown(QUIT):
				print "we are exiting"
				exit(0)
				print "exiting has occured"
				
		if not self.paused:
			self.updateCamera(elapsedTime)
			self.player.move(elapsedTime, self.camera)
			for enemy in self.enemies:
				enemy.move(elapsedTime)
			self.player.detectActions()
			
		
		if self.controlScheme.keyDown(PAUSE):
			if not self.pauseWasPressed:
				print "pause was pressed"
				self.paused = not self.paused
				if not self.controlScheme.ignoreMouseChanges():#ignore all changes to mouse position that occur during pause
					print "mouse problem"
				self.pauseWasPressed = True
		else:
			self.pauseWasPressed = False
			
				
		
		
		
		
		return task.cont
	
	def rotateCamera(self):
		if self.controlScheme.mouseX > self.winProps.getXSize():
			self.camera.setH(-(self.winProps.getXSize() - 20) * 0.5)
			print "camera check 1"
		else:
			self.camera.setH(-self.controlScheme.mouseX * 0.5)
			print "camera check 2"
	
	def updateCamera(self, elapsedTime):
		#update the camera's heading based on the mouse's x position
		if self.controlScheme.recheckMouse():
			print "successful"
			self.camera.setH(-self.controlScheme.mouseX * 0.5)
		else:
			print "recheck failed"
			self.rotateCamera()
			
		
		#update the camera's pitch and vertical position based on the mouse's y position
		self.cameraVOffset = min(self.screenHeight, max(0, self.controlScheme.mouseY)) / self.screenHeight * 25 + 4
		self.cameraHOffset = self.cameraVOffset * 0.8 + 30
		self.camera.setP(atan2(-self.cameraVOffset * 0.7, self.cameraHOffset) \
							* 180 / pi)
		
		#update the camera to point at the player
		self.camera.setPos(self.player.getX() + self.cameraHOffset * sin(self.camera.getH() * pi / 180),
						   self.player.getY() - self.cameraHOffset * cos(self.camera.getH() * pi / 180),
						   self.player.getZ() + 0.3 + self.cameraVOffset)
	
	def gameOver(self):
		pass

if __name__ == '__main__':
	game = Game()
	game.run()
