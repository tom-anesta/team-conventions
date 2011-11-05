from __future__ import division
from sys import exit
import os

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
		
		
		#declare null values for variables, fill them in later
		self.environment = None
		self.player = None
		
		#object lists
		self.enemies = []
		self.obstacles = []
		
		#not paused by default
		self.paused = False
		self.pauseWasPressed = False
		
		#variables for tracking time
		self.previousFrameTime = 0
		
		filename = PARAMS_PATH + "environment.txt"
		self.loadLevelGeom(filename)
		
		
		#load and render the environment model
		'''
		self.environment = self.loader.loadModel(MODELS_PATH + "maya_crater")
		self.environment.reparentTo(self.render)
		self.environment.setScale(0.25, 0.25, 0.25)
		self.environment.setPos(-8, 42, 0)
		'''
		
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
	
	def loadLevelGeom(self, filename):
		#os.chdir("..")
		filename = os.path.abspath(filename)
		if not os.path.isfile(filename):
			print "FILE DOES NOT EXIST"
			exit(1)
		else:
			print "FILE DOES EXIST"
		
		#get the lines from the file
		textFileList = open(filename, 'r').readlines()
		
		if len(textFileList) < 1:
			print "FATAL ERROR READING FILE"
			exit(1)
		else:
			print "READ LINES FROM FILE"
			
		#now split each line into lists
		
		i = 0
		
		for line in textFileList:
			textFileList[i] = line.split(TEXT_DELIMITER)
			for string in textFileList[i]:
				string.strip()#remove whitespace or endlines
			i = i+1
		
		'''
		for list in textFileList:
			for object in list:
				print "obj " + object
		'''
		i = 0
		
		for list in textFileList: #go through the list
			if list[0] == TERRAIN_OUTER:#do all the things for the terrain
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				#this yielded an error
				self.environment = self.loader.loadModel(modelVal)
				#begin fix, didn't work
				#modelVal = os.path.abspath(modelVal)
				#self.environment = self.loader.loadModel(modelVal)
				#end fix
				self.environment.reparentTo(self.render)
				
				#set scale
				scaleVal = list[2]
				scaleVal = scaleVal.split(',')#split by commas
				'''
				for val in scaleVal:
					val = float(val)
					print val
				Sx = scaleVal[0]
				Sy = scaleVal[1]
				Sz = scaleVal[2]
				'''
				self.environment.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3]
				locVal = locVal.split(',')
				for val in locVal:
					val = float(val)
					print val
				self.environment.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#then we have our terrain
			elif list[0] == TERRAIN_OBJECT:
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				self.obstacles.append(obstacle)
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2]
				scaleVal = scaleVal.split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3]
				locVal = locVal.split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				
			else:
				print "FATAL ERROR READING FILE"
				exit(1)
			
		pass
	
	def updateGameTask(self, task):
		elapsedTime = task.time - self.previousFrameTime
		self.previousFrameTime = task.time
		
		if self.controlScheme.keyDown(QUIT):
				exit(0)
				
		if not self.paused:
			self.updateCamera(elapsedTime)
			self.player.move(elapsedTime, self.camera)
			for enemy in self.enemies:
				enemy.move(elapsedTime)
			self.player.detectActions()
			
		
		if self.controlScheme.keyDown(PAUSE):
			if not self.pauseWasPressed:
				self.paused = not self.paused
				self.controlScheme.resetMouse()
				self.pauseWasPressed = True
		else:
			self.pauseWasPressed = False
		
		return task.cont
	
	def rotateCamera(self):
		if self.controlScheme.mouseX > self.winProps.getXSize():
			self.camera.setH(-(self.winProps.getXSize() - 20) * 0.5)
		else:
			self.camera.setH(-self.controlScheme.mouseX * 0.5)
	
	def updateCamera(self, elapsedTime):
		#update the camera's heading based on the mouse's x position
		if self.controlScheme.recheckMouse():
			self.camera.setH(-self.controlScheme.mouseX * 0.5)
		else:
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
