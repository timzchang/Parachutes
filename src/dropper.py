"""
Name: Christopher Syers, Tim Chang
Date: May 2, 2016
CSE30332 Programming Paradigms Final Project

dropper.py

Continuously attempts to make connection to host (shooter.py).
Game starts when a connection is made. Clicks on screen to drop 
cyborgs down to the ground. Game ends when you run out of troops 
to drop, or the shooter runs out of lives.
"""

import math
import os
import sys
import pygame
from pygame.locals import *
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import cPickle as pickle
import zlib
from dropper_obj import *

host = 'localhost'
port = 42668

class ParaConnection(Protocol):
	"""
	ParaConnection: Protocol for connection between the shooter and 
	the dropper. This object will occasionally (24 times a second) 
	send event info to the shooter so it can add new parachuters 
	to the screen. It will receive synchronization data for the 
	current parachuters and the current bullets on the screen, and 
	update the gamespace accordingly
	"""
	def __init__(self, addr, gs):
		"""
		ParaConnection.__init__: initializer that saves the gamespace
		that this connection is working on
		"""
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		"""
		ParaConnection.connectionMade: function called when the 
		connection is opened. When it opens, it starts a looping call 
		that occasionally transmits data about the clicking events. Also
		sets the gamespace's status to 1, indicating that it is ready to 
		play
		"""
		self.lc = LoopingCall(self.gs_pickler)
		self.lc.start(1/24)
		self.gs.conn_status = 1		# indicate that the game is ready to play

	def gs_pickler(self):
		"""
		ParaConnection.gs_pickler: function that is called 24 times a second. 
		Pickles and compresses the gamespace's trans_info, which contains 
		information about the events that have happened. Once it transmits the 
		events, it deletes them from the trans_info buffer.
		"""
		pv = pickle.dumps(self.gs.trans_info)
		pv = zlib.compress(pv)
		self.transport.write(pv)	# writes the pickled, compressed events to the shooter
		del self.gs.trans_info[:]	# clears the event list

	def dataReceived(self, data):
		"""
		ParaConnection.dataReceived: called whenever the shooter sends info about the 
		bullets and parachuters calls an update function in the gamespace to clear the 
		bullets and paarchuters arrays
		"""
		pv = zlib.decompress(data)
		pv = pickle.loads(pv)
		self.gs.update(pv)

	def connectionLost(self, reason):
		"""
		ParaConnection.connectionLost: called when the connection is lost. Changes 
		the conn_status of the gamespace to indicate that the shooter disconnected.
		"""
		self.gs.conn_status = 2


class ParaConnFactory(ReconnectingClientFactory):
	"""
	ParaConnFactory: object that generates paraConnections. Dervies from 
	ReconnectingClientFactory, which will periodically reach out to the 
	host until it gets a connection. Creates a ParaConnection once it connects
	"""
	def __init__(self, gs):
		"""
		ParaConnFactory.__init__: initializer for the ParaConnFactory, sets a 
		data member to store the gasestate instance that this program will use
		"""
		self.gs = gs

	def buildProtocol(self, addr):
		"""
		ParaConnFactory.buildProtocol: function called when the connection is made. 
		Creates a ParaConnection with the gamespace instance passed into the 
		initializer.
		"""
		self.resetDelay()
		return ParaConnection(addr, self.gs)

	def clientConnectionFailed(self, connector, reason):
		"""
		ParaConnFactory.clientConnectionFailed: function that is called when the 
		connectTCP fails to reach the host. Taken from the internet, this function 
		will periodically attempt to connect until the connection is successful.
		"""
		ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class GameSpace:
	"""
	GameSpace: class that holds the game logic and game loop. Has a function that will 
	be called in a looping call that updates everything, handles events, and draw to the 
	screen. 
	"""
	def init(self):
		"""
		GameSpace.init: function that is called to initialize the gamespace instance. Does things 
		like sets up member varaibles for the various images, sets up the various game objects.

		conn_status - flag to tell what state the game is in:
			0: waiting for player 1
			1: playing game
			2: connection lost
			3: won game
			4: lost game
		"""
		pygame.init()									
		self.size = self.wifth, self.height = 640, 480				# screen size
		self.screen = pygame.display.set_mode(self.size)			
		pygame.display.set_caption("Parachutes")					# sets the screen title to "Parachutes"
		self.bg = pygame.image.load("../media/background.png")		
		self.bg = pygame.transform.scale(self.bg, (640,480))		# sets self.bg to an image scaled to the screen size
		self.conn_status = 0										# conn_status starts at 0 to indicate waiting for player 1

		# Creates, scales, places disconnect text image
		self.dc_image = pygame.image.load("../media/dc.png")
		w,h = self.dc_image.get_size()
		scale = .45
		self.dc_image = pygame.transform.scale(self.dc_image, (int(w*scale), int(h*scale)))	# scale it a smaller size
		self.dc_rect = self.dc_image.get_rect()								
		self.dc_rect.center = (320,240)														# center the rectangle in the middle of screen

		# Creates, scales, places waiting text image
		self.wait_image = pygame.image.load("../media/wait_p1.png")
		w,h = self.wait_image.get_size()
		scale = .35
		self.wait_image = pygame.transform.scale(self.wait_image, (int(w*scale), int(h*scale))) # sclae to make it smaller
		self.wait_rect = self.wait_image.get_rect()
		self.wait_rect.center = (320,240)				# center in the screen

		# Creates, scales, places win text image
		self.win_image = pygame.image.load("../media/win.png")
		w,h = self.win_image.get_size()
		scale = .8
		self.win_image = pygame.transform.scale(self.win_image, (int(w*scale), int(h*scale)))
		self.win_rect = self.win_image.get_rect()
		self.win_rect.center = (320,240)

		# Creates, scales, places lose text image
		self.lose_image = pygame.image.load("../media/lose.png")
		w,h = self.lose_image.get_size()
		scale = .8
		self.lose_image = pygame.transform.scale(self.lose_image, (int(w*scale), int(h*scale)))
		self.lose_rect = self.lose_image.get_rect()
		self.lose_rect.center = (320,240)

		# Set up game objects
		self.parachuters = []			# list of parachuters that are currently on the screen
		self.bullets = []				# list of bullets that are currently on the screen
		self.gun = Gun(self)			# creates a gun
		self.turret = Turret(self)		# creates a turret (gun base)
		self.trans_info = []			# array of events that will be transmitted to the shooter 24 times a second
		self.font = pygame.font.Font(None,36) # Font used to render the number of troops remaining at the top of the screen

		# Information about troops remaining
		self.mode = 0						# mode: tells which cyborg type will be dropped when mouse button is clicked
		self.troops = [20,15,15,15,10]		# troops: array of the number of remaining cyborgs of each type
		self.out_of_troops = False			# flag to say whether or not more troops remain


	def game_loop_iterate(self):
		"""
		GameState.game_loop_iterate: function that is called 60 times a second. Does things 
		like update flags, handles user input, and updates list that will be send to the 
		shooter (player 1). Also draws things to the screen using blit.

		Clicks on the screen are handled in this function. Depending on the mode, different
		parachuters are created in the game.
			mode 0: regular colored cyborg, slow moving, 2 hitpoints
			mode 1: purple cyborg, slow moving, 3 hitpoints, teleports when hit
			mode 2: blue cyborg, moves extremely quickly
			mode 3: red cyborg, sways back and forth as it falls
			mode 4: green cyborg, slow moving but has 7 hitpoints
		"""

		# check to see if there are any droops remaining. If there are not,
		# send an indicator to the shooter so it can determine who won the game
		if sum(self.troops) == 0 and self.out_of_troops == False:
			self.out_of_troops = True
			self.trans_info.append("no more troops")

		# handle user input
		for event in pygame.event.get():
			# if the user pressed exit button in the top corner, stop the reactor, thus shutting everything down
			if event.type == QUIT:
				reactor.stop()			# shut everything down
			# only handle clicks when the GameState's conn_status is 1, indicating a game is going on
			if self.conn_status == 1:
				# if the user pressed a mouse button
				if event.type == MOUSEBUTTONDOWN:
					# switch on the mode of the GameState. Every mode produces a different event that is sent to the 
					# shooter, indicating a different type of parachuter. Only produces the troop if there are troops 
					# of that kind remaining. 
					if self.mode == 0:
						if self.troops[0] > 0:
							self.troops[0] -= 1
							self.trans_info.append(((pygame.mouse.get_pos()[0],10),4,"",2,False,0,"left"))
					elif self.mode == 1:
						if self.troops[1] > 0:
							self.troops[1] -= 1
							self.trans_info.append(((pygame.mouse.get_pos()[0],10),4,"purple_",3,False,0,"left"))
					elif self.mode == 2:
						if self.troops[2] > 0:
							self.troops[2] -= 1
							self.trans_info.append(((pygame.mouse.get_pos()[0],10),1,"blue_",2,False,0,"left"))
					elif self.mode == 3:
						if self.troops[3] > 0:
							self.troops[3] -= 1
							self.trans_info.append(((pygame.mouse.get_pos()[0],10),3,"red_",2,True,0,"left"))
					elif self.mode == 4:
						if self.troops[4] > 0:
							self.troops[4] -= 1
							self.trans_info.append(((pygame.mouse.get_pos()[0],10),8,"green_",7,False,0,"left"))
				# if the user pressed a key, check to see if it was the 1, 2, 3, 4, or 5 key. Adjust the mode
				# accoridngly
				if event.type == KEYDOWN:
					if event.key == K_0:	
						self.mode = 0
					elif event.key == K_1:
						self.mode = 1
					elif event.key == K_2:
						self.mode = 2
					elif event.key == K_3:
						self.mode = 3
					elif event.key == K_4:
						self.mode = 4
		
		# initiate a tick on the game objects, so that this screen stays somewhat updated
		# until it gets the new information about the bullets and parachuters. Only activates 
		# when a game is going on
		if self.conn_status == 1:
			self.turret.tick()
			self.gun.tick()
			for parachuter in self.parachuters:
				parachuter.tick()
			for bullet in self.bullets:
				bullet.tick()

		# Display the game objects to the screen
		self.screen.blit(self.bg,(0,0))							# display background first
		for bullet in self.bullets:								# display all the bullets
			self.screen.blit(bullet.image,bullet.rect)	
		self.screen.blit(self.gun.image, self.gun.rect)			# display the gun
		self.screen.blit(self.turret.image,self.turret.rect)	# display the turret
		for parachuter in self.parachuters:						# display each parachuter
			self.screen.blit(parachuter.image,parachuter.rect)

		# Display the number of troops remaining on the screen
		troops_string = "Cyborgs: " + str(self.troops)			# display the word cyborg then the list of remaining troops
		text = self.font.render(troops_string,1,(255,255,255))	# write it as white
		textpos = text.get_rect()
		textpos.centerx = self.bg.get_rect().centerx			# anchor it to the top of the screen
		self.screen.blit(text,textpos)							# display it

		# Depending on the conn_status, display certain messages on the screen
		# if 0, display waiting image
		if self.conn_status == 0:
			self.screen.blit(self.wait_image, self.wait_rect)
		# if 2, display disconnected image
		if self.conn_status == 2:
			self.screen.blit(self.dc_image, self.dc_rect)
		# if 3, display winning image
		if self.conn_status == 3:
			self.screen.blit(self.win_image, self.win_rect)
		# if 4, display losing image
		if self.conn_status == 4:
			self.screen.blit(self.lose_image, self.lose_rect)

		# flip the screen so it is displayed
		pygame.display.flip()

	def update(self, trans_info):
		"""
		GameState.update: function called when data is received from the shooter program. 
		It deletes the parachuters and bullets lists, and repopulates them with the information 
		received from the shooter.
		"""
		del self.parachuters[:]			# clear the native data
		del self.bullets[:]				# clear the native data
		# repopulate the parachuters will every parachuter from the trans_info from shooter
		self.parachuters = [Parachuter(parachuter,self) for parachuter in trans_info["parachuters"]]
		# repopulate the bullets list with every bullets from the trans_info from shooter
		self.bullets = [Bullet((bullet[0].x, bullet[0].y), bullet[1], self) for bullet in trans_info["bullets"]]
		# get the gun positions from the trans_info
		self.gun.rect = trans_info['gun'][0]
		# get the gun angle from the trans_info
		self.gun.theta_d = trans_info['gun'][1]
		# if the shooter program indicates it has lost, this program has won, so set conn_status to 3
		if trans_info['lost'] == 4:
			self.conn_status = 3
		# if the shooter program indicates it has won, this program has lost, so set conn_status to 4
		if trans_info['lost'] == 3:
			self.conn_status = 4

# run this portion if the program is run as main
if __name__ ==  '__main__':
	gs = GameSpace()			# create a GameSpace object 
	gs.init()					# initilizes the object to create game objects
	lc = LoopingCall(gs.game_loop_iterate)	# sets up a looping call to update the GameSpace
	lc.start(1/60)							# call the game_loop_iterate 60 times a second
	reactor.connectTCP(host, port, ParaConnFactory(gs))		# connect host on the host and port
	reactor.run()			# start the reactor to start twisted event loop
