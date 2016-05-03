'''
Name: Christopher Syers, Tim Chang
Date: May 2, 2016
CSE30332 Programming Paradigms Final Project

shooter.py

Waits for a connection from player two (dropper.py) and then 
start a game of parachutes. This player in this file will 
attempts to shoot down the cyborgs that are dropped by the 
other player. The game ends when the dropper is out of cyborgs 
to drop or the shooter runs out of lives, whichever comes first.
'''

import math
import os
import sys
import pygame
import cPickle as pickle
import zlib
from pygame.locals import *
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from defender_obj import *

port = 40040

class ParaConnection(Protocol):
	"""ParaConnection: connection class of shooter. Connect to 
	shooter.py, pass along parachuter creation events"""
	def __init__(self, addr, gs):
		"""__init__: add game state as data member"""
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		"""connectionMade: Once the connection to dropper is made,
			begin pickling parts of the game state to send
			to dropper every 1/24 of a second"""
		self.lc = LoopingCall(self.gs_pickler)
		self.lc.start(1/24)
		self.gs.conn_status = 1  # status: playing

	def gs_pickler(self):
		"""gs_pickler: pickles and sends selections of the gamestate
			saved in trans_info"""
		pv = pickle.dumps(self.gs.trans_info)
		pv = zlib.compress(pv)
		self.transport.write(pv)

	def dataReceived(self, data):
		"""dataReceived: when shooter receives the gamestate from dropper
			it unpacks the data and passes it to the gamestate"""
		pv = zlib.decompress(data)
		pv = pickle.loads(pv)
		self.gs.client_events = pv

	def connectionLost(self, reason):
		"""connectionLost: if the connection to dropper is lost, we 
			cease to call the looping call, and set our
			connection to 2: disconnected"""
		self.gs.conn_status = 2
		self.lc.stop()

class ParaConnFactory(Factory):
	"""ParaConnFactory: a standard connection factory"""
	def __init__(self, gs):
		"""__init__: take in the game state as a member"""
		self.gs = gs

	def buildProtocol(self, addr):
		"""buildProtocol: build a ParaConnection"""
		return ParaConnection(addr, self.gs)

class GameSpace:
	"""GameSpace: where the game logic happens, it takes care of all the 
		assets and game logic"""
	def init(self):
			"""init: initializes all surfaces and objects needed for the game"""
			# 1) screen initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)
			pygame.display.set_caption("Parachutes")
			self.bg = pygame.image.load("../media/background.png")
			self.bg = pygame.transform.scale(self.bg, (640,480))

			# disconnected image - when dropper disconnects, this image shows
			self.dc_image = pygame.image.load("../media/dc.png")
			w,h = self.dc_image.get_size()
			scale = .45
			self.dc_image = pygame.transform.scale(self.dc_image, (int(w*scale), int(h*scale)))
			self.dc_rect = self.dc_image.get_rect()
			self.dc_rect.center = (320,240)
			
			# wait image - at the start before dropper connects, this image shows
			self.wait_image = pygame.image.load("../media/wait_p2.png")
			w,h = self.wait_image.get_size()
			scale = .35
			self.wait_image = pygame.transform.scale(self.wait_image, (int(w*scale), int(h*scale)))
			self.wait_rect = self.wait_image.get_rect()
			self.wait_rect.center = (320,240)

			# win image - shows if dropper wins
			self.win_image = pygame.image.load("../media/win.png")
			w,h = self.win_image.get_size()
			scale = .8
			self.win_image = pygame.transform.scale(self.win_image, (int(w*scale), int(h*scale)))
			self.win_rect = self.win_image.get_rect()
			self.win_rect.center = (320,240)

			# lose image - shows if shooter wins
			self.lose_image = pygame.image.load("../media/lose.png")
			w,h = self.lose_image.get_size()
			scale = .8
			self.lose_image = pygame.transform.scale(self.lose_image, (int(w*scale), int(h*scale)))
			self.lose_rect = self.lose_image.get_rect()
			self.lose_rect.center = (320,240)

			self.turret_lives = 5
			# 0 = waiting
			# 1 = playing
			# 2 = DC
			# 3 = win
			# 4 = lose
			self.conn_status = 0

			# 2) set up game objects
			self.parachuters = []
			self.bullets = []
			self.gun = Gun(self)
			self.turret = Turret(self)

			# information to be sent/received over network
			self.trans_info = {"bullets": [], "parachutes": []}  # sent to dropper
			self.client_events = []  # received from dropper
			self.dropper_out_of_troops = False  # received from dropper

			self.font = pygame.font.Font(None,36)

	def game_loop_iterate(self):
			"""game_loop_iterate: the game loop
				this function takes care of all game logic and
				is called in the looping call"""

			# setting theta to be used by the gun/bullet
			mx, my = pygame.mouse.get_pos()
			O = my - self.turret.rect.center[1]
			A = mx - self.turret.rect.center[0]
			self.theta = math.atan2(-O,float(A))
			if self.theta < 0 and self.theta > -math.pi/2:
				self.theta = 0
			elif self.theta < 0 and self.theta < -math.pi/2:
				self.theta = math.pi

			# 5) user inputs
			# clean bullets and parachuters that have been hit
			self.clean_parachuters()
			self.clean_bullets()

			# set flag to end game when the turret is out of lives
			if self.turret_lives < 0:
				self.conn_status = 4

			for event in pygame.event.get():
				if event.type == QUIT:
					reactor.stop()
				if self.conn_status == 1:
					if event.type == MOUSEBUTTONDOWN:
						self.bullets.append(Bullet(self.theta,self))  # add Bullet

			# 6) send a tick to every game object
			# If status is playing
			if self.conn_status == 1:
				for event in self.client_events:  # dropper is out of troops
					if event == "no more troops":
						self.dropper_out_of_troops = True  # keep track of on screen cyborgs
					else:
						self.parachuters.append(Parachuter(event,self))  # there are troops
				del self.client_events[:]  # clear event list, it will be updated soon
				self.turret.tick()
				self.gun.tick()
				for parachuter in self.parachuters:
					parachuter.tick()
				for bullet in self.bullets:
					bullet.tick()

			# 6.5 update trans_info
			# keep track of bullets,parachutes,gun position, current conn_status
			self.trans_info['bullets'] = [(bullet.rect, bullet.theta) for bullet in self.bullets]
			self.trans_info['parachuters'] = [(parachuter.rect.center,parachuter.speed,parachuter.color,parachuter.hitpoints,parachuter.sway,parachuter.sway_count,parachuter.sway_dir) for parachuter in self.parachuters]
			self.trans_info['gun'] = (self.gun.rect, self.gun.theta_d)
			self.trans_info['lost'] = self.conn_status

			# if dropper is out of troops and no more cyborgs, we win
			if self.dropper_out_of_troops and not self.parachuters:
				self.conn_status = 3

			# 7) display the game objects
			self.screen.blit(self.bg,(0,0))
			for bullet in self.bullets:
				self.screen.blit(bullet.image,bullet.rect)
			self.screen.blit(self.gun.image, self.gun.rect)
			self.screen.blit(self.turret.image,self.turret.rect)
			for parachuter in self.parachuters:
				self.screen.blit(parachuter.image,parachuter.rect)
			
			# lives string
			if self.conn_status == 4:
				lives_string = "Lives: 0"
			else:
				lives_string = "Lives: " + str(self.turret_lives)
			text = self.font.render(lives_string,1,(255,255,255))
			textpos = text.get_rect()
			textpos.centerx = self.bg.get_rect().centerx
			self.screen.blit(text,textpos)
			if self.conn_status == 2:  # disconnected
				self.screen.blit(self.dc_image, self.dc_rect)
			if self.conn_status == 0:  # waiting
				self.screen.blit(self.wait_image, self.wait_rect)
			if self.conn_status == 3:  # win
				self.screen.blit(self.win_image, self.win_rect)
			if self.conn_status == 4:  # lose
				self.screen.blit(self.lose_image, self.lose_rect)
			pygame.display.flip()


	def clean_parachuters(self):
		"""clean_parachuters: clear parachuters that have been 
			shot down/reached bottom of screen, update turret_lives"""
		pre_clean = len(self.parachuters)
		self.parachuters = [value for value in self.parachuters if value.reached_bottom == False]
		post_clean = len(self.parachuters)
		self.turret_lives -= pre_clean - post_clean
		self.parachuters = [value for value in self.parachuters if value.hit == False]

	def clean_bullets(self):
		"""clean_bullets: clear bullets that have gone out of bounds
			or hit a parachuter"""
		self.bullets = [value for value in self.bullets if value.out_of_bounds == False]
		self.bullets = [value for value in self.bullets if value.hit == False]


if __name__ == '__main__':
	gs = GameSpace()
	gs.init()
	lc = LoopingCall(gs.game_loop_iterate)
	lc.start(1/60)
	reactor.listenTCP(port,ParaConnFactory(gs))
	reactor.run()
	lc.stop()
