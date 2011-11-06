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
from pandac.PandaModules import Point2
from panda3d.core import CollisionRay, CollisionNode, GeomNode, CollisionTraverser
from panda3d.core import CollisionHandlerQueue, CollisionSphere, BitMask32
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
		
		#start the collision traverser
		self.cTrav = CollisionTraverser()
		self.cTrav.showCollisions(render)#show the collisions
		
		filename = PARAMS_PATH + "environment.txt"
		self.loadLevelGeom(filename)
		
		#begin code for terrain collisions
		
		#lookup table for actors
		self.actors = {}
		
		#load and render the environment model
		'''
		self.environment = self.loader.loadModel(MODELS_PATH + "maya_crater")
		self.environment.reparentTo(self.render)
		self.environment.setScale(400, 400, 400)
		self.environment.setPos(-8, 42, -80)
		'''
		
		#place the player in the environment
		self.player = Player(self.controlScheme)
		self.player.setName("player")
		self.player.setH(180)
		self.player.reparentTo(self.render)
		self.player.nodePath = self.render.find("player")
		self.playerGroundCol = self.player.find("SleekCraftCollisionRect")
		self.actors["player"] = self.player
		
		#add an enemy
		self.tempEnemy = RushEnemy()
		self.tempEnemy.setPos(-20, 0, 0)
		self.tempEnemy.setName("enemy1")
		self.tempEnemy.reparentTo(self.render)
		self.tempEnemy.nodePath = self.render.find("enemy1")
		self.actors["enemy1"] = self.tempEnemy
		
		self.tempEnemy2 = RushEnemy()
		self.tempEnemy2.setPos(40, 50, 0)
		self.tempEnemy2.setName("enemy2")
		self.tempEnemy2.reparentTo(self.render)
		self.tempEnemy2.nodePath = self.render.find("enemy2")
		self.actors["enemy2"] = self.tempEnemy2
		
		self.tempEnemy3 = RushEnemy()
		self.tempEnemy3.setPos(20, 80, 0)
		self.tempEnemy3.setName("enemy3")
		self.tempEnemy3.reparentTo(self.render)
		self.tempEnemy3.nodePath = self.render.find("enemy3")
		self.actors["enemy3"] = self.tempEnemy3
		
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
		
		#add targeting to the world
		self.setupTargeting()
	
	def loadLevelGeom(self, filename):
		#os.chdir("..")
		filename = os.path.abspath(filename)
		if not os.path.isfile(filename):
			print "FILE DOES NOT EXIST:"
			exit(1)
		
		#get the lines from the file
		textFileList = open(filename, 'r').readlines()
		
		if len(textFileList) < 1:
			print "FATAL ERROR READING FILE"
			exit(1)
			
		#now split each line into lists
		
		i = 0
		
		for line in textFileList:
			textFileList[i] = line.split(TEXT_DELIMITER)
			for string in textFileList[i]:
				string.strip()#remove whitespace or endlines
			i = i + 1
		
		i = 0
		
		for list in textFileList: #go through the list
			if list[0] == TERRAIN_OUTER:#do all the things for the terrain
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				#this yielded an error
				#print modelVal
				self.environment = self.loader.loadModel(modelVal)
				#begin fix, didn't work
				#modelVal = os.path.abspath(modelVal)
				#self.environment = self.loader.loadModel(modelVal)
				#end fix
				self.environment.reparentTo(self.render)
				
				#set scale
				scaleVal = list[2]
				scaleVal = scaleVal.split(',')#split by commas
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
			time = min(0.25, elapsedTime)
			while time > 0.05:
				self.runGame(0.05)
				time -= 0.05
			self.runGame(time)
		if self.controlScheme.keyDown(PAUSE):
			if not self.pauseWasPressed:
				self.paused = not self.paused
				self.controlScheme.resetMouse()
				self.pauseWasPressed = True
		else:
			self.pauseWasPressed = False
		
		return task.cont
	
	def runGame(self, time):
		self.updateCamera(time)
		self.player.move(time, self.camera)
		for enemy in self.enemies:
			enemy.move(time)
		self.player.update(self, time)
	
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
	
	def selectTarget(self):
		"""Finds the closest shootable object and returns it"""

		#traverse all objects in render
		self.mPickerTraverser.traverse(self.render)

		if (self.mCollisionQue.getNumEntries() > 0):
			self.mCollisionQue.sortEntries()
			for i in range(0, self.mCollisionQue.getNumEntries()):
				entry = self.mCollisionQue.getEntry(i)
				pickedObj = entry.getIntoNodePath()
				
				if not pickedObj.isEmpty():
					#here is how you get the surface collsion
					#pos = entry.getSurfacePoint(self.render)
					
					#get the name of the picked object
					name = pickedObj.getParent().getParent().getParent().getName()
					if name=="render":
						return None
					
					#if the object is shootable, set it as the target
					if self.actors[name].shootable:
						print self.actors[name].getName()
						return self.actors[name]
					
					#handlePickedObject(pickedObj)
		
		return None
	
	def setupTargeting(self):
		"""Set up the collisions necessary to target enemies and other objects"""
		
		#Since we are using collision detection to do picking, we set it up 
		#any other collision detection system with a traverser and a handler
		self.mPickerTraverser = CollisionTraverser()            #Make a traverser
		#self.mPickerTraverser.showCollisions(render)
		self.mCollisionQue = CollisionHandlerQueue()

		#create a collision solid ray to detect against
		self.mPickRay = CollisionRay()
		self.mPickRay.setOrigin(self.player.getPos(self.render))
		self.mPickRay.setDirection(self.render.getRelativeVector(self.player, Vec3(0, 1, 0)))

		#create our collison Node to hold the ray
		self.mPickNode = CollisionNode('pickRay')
		self.mPickNode.addSolid(self.mPickRay)

		#Attach that node to the player since the ray will need to be positioned
		#relative to it, returns a new nodepath		
		#well use the default geometry mask
		#this is inefficent but its for mouse picking only

		self.mPickNP = self.player.attachNewNode(self.mPickNode)

		#well use what panda calls the "from" node.  This is really a silly convention
		#but from nodes are nodes that are active, while into nodes are usually passive environments
		#this isnt a hard rule, but following it usually reduces processing

		#Everything to be picked will use bit 1. This way if we were doing other
		#collision we could seperate it, we use bitmasks to determine what we check other objects against
		#if they dont have a bitmask for bit 1 well skip them!
		self.mPickNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

		#Register the ray as something that can cause collisions
		self.mPickerTraverser.addCollider(self.mPickNP, self.mCollisionQue)
		#if you want to show collisions for debugging turn this on
		#self.mPickerTraverser.showCollisions(self.render)
	#END ATTEMPT AT AUTO-TARGETING
	
	def gameOver(self):
		pass

if __name__ == '__main__':
	game = Game()
	game.run()
