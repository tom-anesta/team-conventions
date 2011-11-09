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
from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionRay, CollisionNode, GeomNode, CollisionTraverser
from panda3d.core import CollisionHandlerQueue, CollisionSphere, BitMask32
from math import pi, sin, cos, sqrt, pow, atan2
from pandac.PandaModules import BitMask32
from pandac.PandaModules import TextNode
from direct.gui.OnscreenImage import OnscreenImage

from unit import Unit
from player import Player
from projectile import Projectile
from bullet import Bullet
from rushEnemy import RushEnemy
from droneEnemy import DroneEnemy
from shootingEnemy import ShootingEnemy
from constants import *
from controlScheme import ControlScheme

class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		#start the time
		self.globalTime = 0
		self.nextEnemy = 1
		
		#setup your collision event handlers, apparently needs a direct object
		
		self.do = DirectObject()
		self.do.accept('unit-into-unit', self.handleUnitIntoCollision)
		self.do.accept('unit-out-unit', self.handleUnitOutCollision)
		self.do.accept('unit-into-cube', self.handleCubeIntoCollision)
		self.do.accept('unit-into-wing', self.handleWingIntoCollision)
		self.do.accept('unit-into-bar', self.handleBarIntoCollision)
		
		#get window properties
		self.winProps = WindowProperties()
		#self.winProps.setFullscreen(True)
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
		self.projectiles = []
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
		self.cTrav.showCollisions(self.render)
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
		
		
		#add some lights
		topLight = DirectionalLight("top light")
		topLight.setColor(Vec4(0.5, 0.5, 0.5, 1))
		topLight.setDirection(Vec3(0, -90, 0))
		self.render.setLight(self.render.attachNewNode(topLight))
		
		ambientLight = AmbientLight("ambient light")
		ambientLight.setColor(Vec4(0.5, 0.5, 0.5, 1))
		self.render.setLight(self.render.attachNewNode(ambientLight))
		
		#the distance the camera is from the player
		self.cameraHOffset = 45
		self.cameraVOffset = 10
		
		#register the update task
		self.taskMgr.add(self.updateGame, "updateGame")
		
		#add targeting to the world
		self.setupTargeting()
		
		# configure the entire GUI
		self.setupGUI()
	
	def setupGUI(self):
		GUIFont = loader.loadFont(FONTS_PATH+'orbitron-black.ttf')
		
		"""
		self.energyBarText = TextNode('node name')
		self.energyBarText.setText("Energy: "+str((100*self.player.energy/self.player.maxEnergy))+"%")
		self.energyBarText.setAlign(TextNode.ALeft)
		self.energyBarText.setFont(GUIFont)
		
		textNodePath = aspect2d.attachNewNode(self.energyBarText)
		textNodePath.setScale(0.08)
		textNodePath.setPos(-1.3333, 0, 1)
		"""
		
		#image is 365 x 187
		self.attackModeImage = OnscreenImage()
		self.attackModeImage.setImage(GUI_PATH+"mode-area.png")
		self.attackModeImage.setTransparency(1)
		
		modeNodePath = aspect2d.attachNewNode(self.attackModeImage.node())
		modeNodePath.setScale(.136631, 0, .07)
		modeNodePath.setPos(-1.13, 0, 0.88)
		
		self.energyBarImage = OnscreenImage()
		self.energyBarImage.setImage(GUI_PATH+"energy-bar-full.png")
		self.energyBarImage.setTransparency(1)
		
		eBarNodePath = aspect2d.attachNewNode(self.energyBarImage.node())
		eBarNodePath.setScale(.400, 0, .0475)
		eBarNodePath.setPos(-0.66, 0, 0.88)
		
		self.healthBarImage = OnscreenImage()
		self.healthBarImage.setImage(GUI_PATH+"health-bar-full.png")
		self.healthBarImage.setTransparency(1)
		
		hBarNodePath = aspect2d.attachNewNode(self.healthBarImage.node())
		hBarNodePath.setScale(.400, 0, .0475)
		hBarNodePath.setPos(0.85, 0, 0.88)
	
	def updateGUI(self):
		
		if self.player.currentWeapon == AREA:
			modeImg = "mode-area"
		elif self.player.currentWeapon == NARROW:
			modeImg = "mode-narrow"
		
		self.attackModeImage.setImage(GUI_PATH+modeImg+".png")
		self.attackModeImage.setTransparency(1)
	
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
				self.environment.setCollideMask(BitMask32.allOff())
				self.craterCollision.setCollideMask(BitMask32(TERRAIN_RAY_MASK))
				
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
				
				
			elif list[0] == TERRAIN_CUBE:
				#choose the model
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2].split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				hprVal = list[4].split(',')
				obstacle.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
				#set up collisions
				unitCollision = obstacle.find("**/CubeBlock")
				unitCollision.node().setName("cube")
				obstacle.setCollideMask(BitMask32.allOff())
				unitCollision.setCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
				
				self.obstacles.append(obstacle)
				
			elif list[0] == TERRAIN_WING:
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2].split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				hprVal = list[4].split(',')
				obstacle.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
				#set up collisions
				unitCollision = obstacle.find("**/wingCollider")
				unitCollision.node().setName("wing")
				obstacle.setCollideMask(BitMask32.allOff())
				unitCollision.setCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
				
				self.obstacles.append(obstacle)
				
			elif list[0] == TERRAIN_BAR:
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2].split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				hprVal = list[4].split(',')
				obstacle.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
				#set up collisions
				unitCollision = obstacle.find("**/metalBarCollisionCube")
				unitCollision.node().setName("bar")
				obstacle.setCollideMask(BitMask32.allOff())
				unitCollision.setCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
				
			elif list[0] == TERRAIN_SHARDS:
				modelVal = list[1]
				modelVal = (MODELS_PATH + modelVal)
				#load the model
				obstacle = self.loader.loadModel(modelVal)
				
				obstacle.reparentTo(render)
				#set scale
				scaleVal = list[2].split(',')
				obstacle.setScale(float(scaleVal[0]), float(scaleVal[1]), float(scaleVal[2]))
				#set location
				locVal = list[3].split(',')
				obstacle.setPos(float(locVal[0]), float(locVal[1]), float(locVal[2]))#the we have our object
				hprVal = list[4].split(',')
				obstacle.setHpr(float(hprVal[0]), float(hprVal[1]), float(hprVal[2]))
				
				#set up collisions
				unitCollision = obstacle.find("**/metalShardCollisionCube")
				unitCollision.node().setName("shard")
				obstacle.setCollideMask(BitMask32.allOff())
				unitCollision.setCollideMask(BitMask32(PLAYER_ENEMY_OBJECTS))
				
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
		
		for val in textFileList:
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
			elif val[0] == DRONE_ENEMY:
				currEnem = dict()
				pos = []
				pos = val[1].split(',')#get the three values for spawning, not floats
				currEnem["type"] = DRONE_ENEMY
				currEnem["xVal"] = float(pos[0])
				currEnem["yVal"] = float(pos[1])
				currEnem["zVal"] = float(pos[2])
				currwave["enemies"].append(dict(currEnem))#copy
			elif val[0] == SHOOTING_ENEMY:
				currEnem = dict()
				pos = []
				pos = val[1].split(',')#get the three values for spawning, not floats
				currEnem["type"] = SHOOTING_ENEMY
				currEnem["xVal"] = float(pos[0])
				currEnem["yVal"] = float(pos[1])
				currEnem["zVal"] = float(pos[2])
				currwave["enemies"].append(dict(currEnem))#copy
			elif val[0] == END_WAVE:#then we are done with that wave
				self.eSpawnList.append(dict(currwave))#copy
			else:
				pass#then something was stupid
			
		#now sort your waves with lowest time first	
		self.eSpawnList.sort(key = lambda object: object["time"])
		#and you're done
	
	def updateGame(self, task):
		self.globalTime = self.globalTime + task.time
		elapsedTime = task.time - self.previousFrameTime
		
		if self.controlScheme.keyDown(QUIT):
			exit(0)
		
		if not self.paused:
			time = elapsedTime
			while time > 0.02:
				self.updateGameComponents(0.02)
				time -= 0.02
			self.updateGameComponents(time)
			
			self.cTrav.traverse(render)
			self.spawnEnemies()#globalTime is available
		if self.controlScheme.keyDown(PAUSE):
			if not self.pauseWasPressed:
				self.paused = not self.paused
				self.controlScheme.resetMouse()
				self.pauseWasPressed = True
		else:
			self.pauseWasPressed = False
		
		self.updateGUI()
		
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
		for projectile in self.projectiles:
			projectile.update(time)
			
		#check for basic terrain collisions
		self.player.terrainCollisionCheck()
		self.player.update(time)
		for enemy in self.enemies:
			enemy.terrainCollisionCheck()
		for projectile in self.projectiles:
			projectile.terrainCollisionCheck()
		
	def spawnEnemies(self):#now we spawn our enemies
		while((len(self.eSpawnList) > 0) and self.eSpawnList[0]["time"] < self.globalTime):
			for val in self.eSpawnList[0]["enemies"]:
				if val["type"] == RUSH_ENEMY:
					#add an enemy
					tempEnemy = RushEnemy(self, val["xVal"], val["yVal"], val["zVal"])
					self.configureEnemy(tempEnemy)
				elif val["type"] == DRONE_ENEMY:
					#add an enemy
					tempEnemy = DroneEnemy(self, self.player, val["xVal"], val["yVal"], val["zVal"])
					self.configureEnemy(tempEnemy)
				elif val["type"] == SHOOTING_ENEMY:
					#add an enemy
					tempEnemy = ShootingEnemy(self, val["xVal"], val["yVal"], val["zVal"])
					self.configureEnemy(tempEnemy)
				else: 
					pass
				
			del self.eSpawnList[0]#del
			
	
	def configureEnemy(self, tempEnemy):#after making an enemy configure it for the game
		numString = str(self.nextEnemy)
		tempEnemy.setName("enemy" + numString)
		tempEnemy.reparentTo(self.unitNodePath)
		tempEnemy.nodePath = self.render.find("enemy1")
		self.actors["enemy" + numString] = tempEnemy
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
				
					name = pickedObj.getParent().getName()
					
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
		self.mPickerTraverser.showCollisions(self.unitNodePath)
		self.mCollisionQue = CollisionHandlerQueue()

		#create a collision solid ray to detect against
		self.mPickRay = CollisionRay()
		self.mPickRay.setOrigin(self.player.getPos(self.render))
		self.mPickRay.setDirection(self.render.getRelativeVector(self.player, Vec3(0, 1, 0)))
		self.mPickRay2 = CollisionRay()
		self.mPickRay2.setOrigin(self.player.getPos(self.render))
		self.mPickRay2.setDirection(self.render.getRelativeVector(self.player, Vec3(0.06, 1, 0)))
		self.mPickRay3 = CollisionRay()
		self.mPickRay3.setOrigin(self.player.getPos(self.render))
		self.mPickRay3.setDirection(self.render.getRelativeVector(self.player, Vec3(-0.06, 1, 0)))
		self.mPickRay4 = CollisionRay()
		self.mPickRay4.setOrigin(self.player.getPos(self.render))
		self.mPickRay4.setDirection(self.render.getRelativeVector(self.player, Vec3(0, 1, 0.06)))
		self.mPickRay5 = CollisionRay()
		self.mPickRay5.setOrigin(self.player.getPos(self.render))
		self.mPickRay5.setDirection(self.render.getRelativeVector(self.player, Vec3(0, 1, -0.06)))

		#create our collison Node to hold the ray
		self.mPickNode = CollisionNode('pickRay')
		self.mPickNode.setIntoCollideMask(BitMask32.allOff())
		self.mPickNode.addSolid(self.mPickRay)
		self.mPickNode2 = CollisionNode('pickRay2')
		self.mPickNode2.setIntoCollideMask(BitMask32.allOff())
		self.mPickNode2.addSolid(self.mPickRay2)
		self.mPickNode3 = CollisionNode('pickRay3')
		self.mPickNode3.setIntoCollideMask(BitMask32.allOff())
		self.mPickNode3.addSolid(self.mPickRay3)
		self.mPickNode4 = CollisionNode('pickRay4')
		self.mPickNode4.setIntoCollideMask(BitMask32.allOff())
		self.mPickNode4.addSolid(self.mPickRay4)
		self.mPickNode5 = CollisionNode('pickRay5')
		self.mPickNode5.setIntoCollideMask(BitMask32.allOff())
		self.mPickNode5.addSolid(self.mPickRay5)

		#Attach that node to the player since the ray will need to be positioned
		#relative to it, returns a new nodepath		
		#well use the default geometry mask
		#this is inefficent but its for mouse picking only

		self.mPickNP = self.player.attachNewNode(self.mPickNode)
		self.mPickNP2 = self.player.attachNewNode(self.mPickNode2)
		self.mPickNP3 = self.player.attachNewNode(self.mPickNode3)
		self.mPickNP4 = self.player.attachNewNode(self.mPickNode4)
		self.mPickNP5 = self.player.attachNewNode(self.mPickNode5)

		#well use what panda calls the "from" node.  This is really a silly convention
		#but from nodes are nodes that are active, while into nodes are usually passive environments
		#this isnt a hard rule, but following it usually reduces processing

		#Everything to be picked will use bit 1. This way if we were doing other
		#collision we could seperate it, we use bitmasks to determine what we check other objects against
		#if they dont have a bitmask for bit 1 well skip them!
		#self.mPickNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
		self.mPickNode.setFromCollideMask(PLAYER_ENEMY_OBJECTS)
		self.mPickNode2.setFromCollideMask(PLAYER_ENEMY_OBJECTS)
		self.mPickNode3.setFromCollideMask(PLAYER_ENEMY_OBJECTS)
		self.mPickNode4.setFromCollideMask(PLAYER_ENEMY_OBJECTS)
		self.mPickNode5.setFromCollideMask(PLAYER_ENEMY_OBJECTS)

		#Register the ray as something that can cause collisions
		self.mPickerTraverser.addCollider(self.mPickNP, self.mCollisionQue)
		self.mPickerTraverser.addCollider(self.mPickNP2, self.mCollisionQue)
		self.mPickerTraverser.addCollider(self.mPickNP3, self.mCollisionQue)
		self.mPickerTraverser.addCollider(self.mPickNP4, self.mCollisionQue)
		self.mPickerTraverser.addCollider(self.mPickNP5, self.mCollisionQue)
		#self.cTrav.addCollider(self.mPickNP, self.mCollisionQue)
		#if you want to show collisions for debugging turn this on
		#self.mPickerTraverser.showCollisions(self.render)
	#END ATTEMPT AT AUTO-TARGETING
	
	def handleUnitIntoCollision(self, entry):
		try:
			fromName = entry.getFromNodePath().getParent().getName()
			intoName = entry.getIntoNodePath().getParent().getName()
			Unit.collideWithUnit(self.actors[intoName], self.actors[fromName])
		except:
			pass
	
	def handleUnitOutCollision(self, entry):
		pass
	
	def handleWingIntoCollision(self, entry):
		fromName = entry.getFromNodePath().getParent().getName()
		Unit.collideWithObstacle(self.actors[fromName])
	
	def handleCubeIntoCollision(self, entry):
		fromName = entry.getFromNodePath().getParent().getName()
		Unit.collideWithObstacle(self.actors[fromName])
	
	def handleBarIntoCollision(self, entry):
		fromName = entry.getFromNodePath().getParent().getName()
		Unit.collideWithObstacle(self.actors[fromName])
	
	def gameOver(self):
		pass

#start the game
if __name__ == '__main__':
	game = Game()
	game.run()
