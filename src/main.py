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
from pandac.PandaModules import NodePath
from pandac.PandaModules import Point2
from panda3d.core import CollisionRay, CollisionNode, GeomNode, CollisionTraverser
from panda3d.core import CollisionHandlerQueue, CollisionSphere, BitMask32
from math import pi, sin, cos, sqrt, pow, atan2
from pandac.PandaModules import BitMask32

from unit import Unit
from player import Player
from rushEnemy import RushEnemy
from constants import *
from controlScheme import ControlScheme

class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		#start the time
		self.globalTime = 0
		self.nextEnemy =1
		
		
		
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
		
		#a node for holding all in-game units
		self.unitNodePath = NodePath('unit holder')
		self.unitNodePath.reparentTo(self.render)
		
		#object lists
		self.enemies = []
		self.obstacles = []
		#list of enemies to be spawned
		self.eSpawnList = []
		
		#not paused by default
		self.paused = False
		self.pauseWasPressed = False
		
		#variables for tracking time
		self.previousFrameTime = 0
		
		#start the collision traverser
		traverser = CollisionTraverser()
		base.cTrav = traverser#run every frame
		self.cTrav = base.cTrav
		#self.cTrav.showCollisions(self.unitNodePath)#show the collisions
		
		#load terrain and enemies
		
		#load the environment, it seems that an x value of zero, a y value of -50 puts the origin point relatively in the middle of the crater
		filename = PARAMS_PATH + "environment.txt"
		self.loadLevelGeom(filename)
		#load the enemies
		filename = PARAMS_PATH + "enemies.txt"
		self.loadLevelEnemies(filename)
		
		#lookup table for actors
		self.actors = {}
		
		#place the player in the environment
		self.player = Player(self.controlScheme, self.camera, self, 0, 0, 0)
		self.player.setName("player")
		self.player.setH(180)
		self.player.reparentTo(self.unitNodePath)
		self.player.nodePath = self.render.find("player")
		self.actors["player"] = self.player
		
		#this should be gone soon
		'''
		#add an enemy
		self.tempEnemy = RushEnemy(self, -20, 0, 0)
		#self.tempEnemy.setPos(-20, 0, 0)
		self.tempEnemy.setName("enemy1")
		self.tempEnemy.reparentTo(self.unitNodePath)
		self.tempEnemy.nodePath = self.render.find("enemy1")
		self.actors["enemy1"] = self.tempEnemy
		
		self.tempEnemy2 = RushEnemy(self, 40, 50, 0)
		#self.tempEnemy2.setPos(40, 50, 0)
		self.tempEnemy2.setName("enemy2")
		self.tempEnemy2.reparentTo(self.unitNodePath)
		self.tempEnemy2.nodePath = self.render.find("enemy2")
		self.actors["enemy2"] = self.tempEnemy2
		
		self.tempEnemy3 = RushEnemy(self, 20, 80, 0)
		#self.tempEnemy3.setPos(20, 80, 0)
		self.tempEnemy3.setName("enemy3")
		self.tempEnemy3.reparentTo(self.unitNodePath)
		self.tempEnemy3.nodePath = self.render.find("enemy3")
		self.actors["enemy3"] = self.tempEnemy3
		
		self.enemies.append(self.tempEnemy)
		self.enemies.append(self.tempEnemy2)
		self.enemies.append(self.tempEnemy3)
		
		for enemy in self.enemies:
			enemy.registerCollider(self.cTrav)
		'''
		
		#add some lights
		topLight = DirectionalLight("top light")
		#topLight.setColor(Vec4(255/255, 253/255, 222/255, 1))
		topLight.setColor(Vec4(255/255, 255/255, 255/255, 1))
		topLight.setDirection(Vec3(0, -90, 0))
		self.render.setLight(self.render.attachNewNode(topLight))
		
		
		ambientLight = AmbientLight("ambient light")
		ambientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
		self.render.setLight(self.render.attachNewNode(ambientLight))
		
		#the distance the camera is from the player
		self.cameraHOffset = 45
		self.cameraVOffset = 10
		
		#register the update task
		self.taskMgr.add(self.updateGame, "updateGame")
		
		#add targeting to the world
		self.setupTargeting()
	
	def loadLevelGeom(self, filename):
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
		
		
		for num, val in enumerate(textFileList):
			val = val.rstrip('\n')#strip the newlines
			val = val.strip()
			textFileList[num] = val.split(TEXT_DELIMITER)
		
		
		obstacle = None
		
		for list in textFileList: #go through the list
			if list[0] == TERRAIN_OUTER:#do all the things for the terrain
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				
				self.environment = self.loader.loadModel(modelVal)
				
				self.environment.reparentTo(self.render)
				
				#get the collision geometry for the environment
				#and move it up a bit to allow the character to float above the crater
				self.craterCollision = self.environment.find("**/craterCollisionPlane")
				self.craterCollision.setZ(self.environment.getZ() + 0.15)
				
				#self.environment.find( #.find("craterCollisionPlane").setZ(self.environment.getZ() + 10)
				
				#set scale
				scaleVal = list[2].split(',')#split by commas
				self.environment.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				self.environment.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#then we have our terrain
				#set rotation
				hprVal = list[4].split(',')
				self.environment.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
				
			elif list[0] == TERRAIN_OBJECT:
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				self.obstacles.append(obstacle)
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2].split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				hprVal = list[4].split(',')
				obstacle.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
			else:
				print "FATAL ERROR READING FILE"
				exit(1)
			
		pass
		
	def loadLevelEnemies(self, filename):
		filename = os.path.abspath(filename)
		if not os.path.isfile(filename):
			print "FILE DOES NOT EXIST:"
			exit(1)
		
		#get the lines from the file and split them
		textFileList = open(filename, 'r').readlines()
		if len(textFileList) < 1:
			print "FATAL ERROR READING FILE"
			exit(1)
		
		for num, val in enumerate(textFileList):
			val = val.rstrip('\n')#strip the newlines
			val = val.strip()
			textFileList[num] = val.split(TEXT_DELIMITER)
		
		currwave = dict()
		currwave["time"] = None
		currwave["enemies"] = []
		currEnem = dict()
		
		print "populating enemy waves"
		
		
		for val in textFileList:
			print val
			if val[0] == BEGIN_WAVE:
				currwave = dict()
				currwave["time"] = float(val[1])#set your time
				currwave["enemies"] = []
			elif val[0] == RUSH_ENEMY:
				currEnem = dict()
				pos = []
				pos = val[1].split(',')#get the three values for spawning, not floats
				currEnem["type"] = RUSH_ENEMY
				currEnem["xVal"] = float(pos[0])
				currEnem["yVal"] = float(pos[1])
				currEnem["zVal"] = float(pos[2])
				currwave["enemies"].append(dict(currEnem))#copy
			elif val[0] == END_WAVE:#then we are done with that wave
				self.eSpawnList.append(dict(currwave))#copy
				print len(self.eSpawnList)
				print "test"
			else:
				pass#then something was stupid
			
		#now sort your waves with lowest time first	
		self.eSpawnList.sort(key = lambda object: object["time"])
		#and you're done
		
		i = 0
		'''
		while i != len(self.eSpawnList):
			print i
			print self.eSpawnList[i]["time"]
			for val in self.eSpawnList[i]["enemies"]:
				print val["type"]
			i = i+1
		'''
	
	def updateGame(self, task):
		self.globalTime = self.globalTime + task.time
		elapsedTime = task.time - self.previousFrameTime
		
		if self.controlScheme.keyDown(QUIT):
			exit(0)
		
		if not self.paused:
			self.updateGameComponents(elapsedTime)
			self.spawnEnemies()#globalTime is available
		if self.controlScheme.keyDown(PAUSE):
			if not self.pauseWasPressed:
				self.paused = not self.paused
				self.controlScheme.resetMouse()
				self.pauseWasPressed = True
		else:
			self.pauseWasPressed = False
		
		self.previousFrameTime = task.time
		
		return task.cont
	
	def updateGameComponents(self, time):
		'''
		Updates the state of the world.
		@precondition: The game isn't paused. 
		'''
		self.updateCamera(time)
		for enemy in self.enemies:
			enemy.update(time)
			
		#check for basic terrain collisions
		self.player.terrainCollisionCheck()
		self.player.update(time)
		for enemy in self.enemies:
			enemy.terrainCollisionCheck()
		
		self.cTrav.traverse(render)
		
		
	def spawnEnemies(self):#now we spawn our enemies
		while(( len(self.eSpawnList) > 0) and self.eSpawnList[0]["time"] < self.globalTime):
			for val in self.eSpawnList[0]["enemies"]:
				if val["type"] == RUSH_ENEMY:
					print "rush enemy"
					#add an enemy
					tempEnemy = RushEnemy(self, val["xVal"], val["yVal"], val["zVal"])
					self.configureEnemy(tempEnemy)
				else: 
					pass
				
			del self.eSpawnList[0]#del
			
	
	def configureEnemy(self, tempEnemy):#after making an enemy configure it for the game
		numString = str(self.nextEnemy)
		tempEnemy.setName("enemy"+numString)
		tempEnemy.reparentTo(self.unitNodePath)
		tempEnemy.nodePath = self.render.find("enemy1")
		self.actors["enemy"+numString] = tempEnemy
		tempEnemy.registerCollider(self.cTrav)
		self.nextEnemy = self.nextEnemy + 1
		self.enemies.append(tempEnemy)
		
	
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
		self.mPickerTraverser.traverse(self.unitNodePath)

		if (self.mCollisionQue.getNumEntries() > 0):
			self.mCollisionQue.sortEntries()
			for i in range(0, self.mCollisionQue.getNumEntries()):
				entry = self.mCollisionQue.getEntry(i)
				pickedObj = entry.getIntoNodePath()
				
				if not pickedObj.isEmpty():
					
					found = False
					
					if pickedObj.getName() != "enemyCollisionSphere":
						continue
					
					name = pickedObj.getParent().getParent().getParent().getName()
					
					if name == "render":
						return None
					
					#if the object is shootable, set it as the target
					if self.actors[name].shootable:
						return self.actors[name]
		
		return None
	
	def setupTargeting(self):
		"""Set up the collisions necessary to target enemies and other objects"""
		
		#Since we are using collision detection to do picking, we set it up 
		#any other collision detection system with a traverser and a handler
		self.mPickerTraverser = CollisionTraverser()            #Make a traverser
		#self.mPickerTraverser.showCollisions(self.unitNodePath)
		self.mCollisionQue = CollisionHandlerQueue()

		#create a collision solid ray to detect against
		self.mPickRay = CollisionRay()
		self.mPickRay.setOrigin(self.player.getPos(self.render))
		self.mPickRay.setDirection(self.render.getRelativeVector(self.player, Vec3(0, 1, 0)))

		#create our collison Node to hold the ray
		self.mPickNode = CollisionNode('pickRay')
		self.mPickNode.setIntoCollideMask(BitMask32.allOff())
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
		#self.mPickNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
		self.mPickNode.setFromCollideMask(BitMask32.bit(0))

		#Register the ray as something that can cause collisions
		self.mPickerTraverser.addCollider(self.mPickNP, self.mCollisionQue)
		#self.cTrav.addCollider(self.mPickNP, self.mCollisionQue)
		#if you want to show collisions for debugging turn this on
		#self.mPickerTraverser.showCollisions(self.render)
	#END ATTEMPT AT AUTO-TARGETING
	
	def gameOver(self):
		pass

#start the game
if __name__ == '__main__':
	game = Game()
	game.run()
