from __future__ import division

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import MouseButton
from pandac.PandaModules import KeyboardButton

from constants import *

class ControlScheme(DirectObject):
	'''
	Handles relatively complex control schemes, allowing multiple keys to
	be assigned to an action. Additionally handles getting the mouse
	position in the world's coordinate space.
	'''
	
	def __init__(self, inputWatcher, window, defaultKeys = []):
		'''
		Creates a new ControlScheme object.
		@param inputWatcher: The MouseWatcher object to use for tracking
		the mouse and keys.
		@param defaultKeys: is a collection of key types to be initialized
		by default (optional). Acceptable values are "left", "right", "up",
		"down", and "pause". The defaults for directional keys are the
		arrows, WASD, and the equivalents of WASD on common alternate
		keyboard layouts. The keys for "pause" are escape, p, and
		enter.
		'''
		self.inputWatcher = inputWatcher
		self.window = window
		properties = window.getProperties()
		self.centerX = properties.getXSize() // 2
		self.prevMouseX = self.centerX
		
		self.keyMap = dict()
		
		self.addKeys(LEFT, [KeyboardButton.left(), KeyboardButton.asciiKey('a'), KeyboardButton.asciiKey('q')])
		self.addKeys(RIGHT, [KeyboardButton.right(), KeyboardButton.asciiKey('d'), KeyboardButton.asciiKey('e')])
		self.addKeys(UP, [KeyboardButton.up(), KeyboardButton.asciiKey('w'), KeyboardButton.asciiKey('z'), KeyboardButton.asciiKey(',')])
		self.addKeys(DOWN, [KeyboardButton.down(), KeyboardButton.asciiKey('s'), KeyboardButton.asciiKey('o')])
		self.addKeys(PAUSE, [KeyboardButton.escape(), KeyboardButton.asciiKey('p'), KeyboardButton.enter()])
		self.addKeys(SWITCH, [KeyboardButton.shift(), KeyboardButton.control(), KeyboardButton.asciiKey('f'), KeyboardButton.asciiKey('/'), MouseButton.two(), KeyboardButton.space()])
		self.addKeys(PUSH, [MouseButton.one()])
		self.addKeys(PULL, [MouseButton.three()])
		self.addKeys(QUIT, [KeyboardButton.asciiKey('q')])
		
		#in case the mouse leaves the window
		self.mouseX = 0
		self.mouseY = 0
			
	
	def addKeys(self, keyType, keys = []):
		'''
		Registers all given keys as keyType.
		@param keyType: A string representing the type of key to register.
		The contents of this string don't matter, as long as you are
		consistent when referencing it later.
		@param keys: An array of ButtonHandle objects to register. For
		convenience, use the KeyboardButton class to define these handles
		(for example, KeyboardButton.backspace() returns a ButtonHandle for
		the backspace key, and KeyboardButton.asciiKey('j') returns a
		handle for the J key.
		'''
		if keyType in self.keyMap:
			self.keyMap.get(keyType).addKeys(keys)
		else:
			self.keyMap[keyType] = KeyGroup(keys)
	
	def keyDown(self, keyType):
		'''
		@param keyType: A string representing the type of key to look up.
		This should match one of the key types passed to the class
		constructor or to addKeys.
		@return: Whether a key of the given type is pressed.
		'''
		if not keyType in self.keyMap:
			return False
		
		return self.keyMap.get(keyType).keyDown(self.inputWatcher)
	
	def recheckMouse(self):
		'''
		@return: Whether it successfully locked the mouse to the center of the screen.
		'''
		pointer = self.window.getPointer(0)
		self.mouseX += pointer.getX() - self.prevMouseX
		self.mouseY = pointer.getY()
		
		if not self.window.movePointer(0, self.centerX, self.mouseY):
			self.prevMouseX = self.mouseX
			return False
		
		return True
		
	def ignoreMouseChanges(self):
		if not self.window.movePointer(0, self.mouseX, self.mouseY):# we want to reset the pointer to the position of the mouse
			return False
			
		return True

class KeyGroup(object):
	'''
	Private - you do not need to reference this outside of ControlScheme.
	'''
	
	def __init__(self, keys):
		#make a copy of the input
		self.keys = [k for k in keys]
	
	def addKeys(self, keys):
		for k in keys:
			if not k in self.keys:
				self.keys.append(k)
	
	def keyDown(self, inputWatcher):
		for k in self.keys:
			if inputWatcher.isButtonDown(k):
				return True
		
		return False
