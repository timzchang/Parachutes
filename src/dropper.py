'''
Name: Christopher Syers, Tim Chang
Date: May 2, 2016
CSE30332 Programming Paradigms Final Project

dropper.py

Continuously attempts to make connection to host (shooter.py).
Game starts when a connection is made. Clicks on screen to drop 
cyborgs down to the ground. Game ends when you run out of troops 
to drop, or the shooter runs out of lives.
'''

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


class ParaConnection(Protocol):
	def __init__(self, addr, gs):
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		# print "connection made"
		self.lc = LoopingCall(self.gs_pickler)
		self.lc.start(1/24)
		self.gs.conn_status = 1

	def gs_pickler(self):
		pv = pickle.dumps(self.gs.trans_info)
		pv = zlib.compress(pv)
		self.transport.write(pv)
		del self.gs.trans_info[:]

	def dataReceived(self, data):
		pv = zlib.decompress(data)
		pv = pickle.loads(pv)
		self.gs.update(pv)

	def connectionLost(self, reason):
		# print "connection lost: ", reason
		self.gs.conn_status = 2


class ParaConnFactory(ReconnectingClientFactory):
	def __init__(self, gs):
		self.gs = gs

	def buildProtocol(self, addr):
		self.resetDelay()
		return ParaConnection(addr, self.gs)

	def clientConnectionFailed(self, connector, reason):
		# print "retry connection"
		ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class GameSpace:
	def init(self):
			# 1) basic initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)
			pygame.display.set_caption("Parachutes")
			self.bg = pygame.image.load("../media/background.png")
			self.bg = pygame.transform.scale(self.bg, (640,480))
			self.conn_status = 0

			# dc image
			self.dc_image = pygame.image.load("../media/dc.png")
			w,h = self.dc_image.get_size()
			scale = .45
			self.dc_image = pygame.transform.scale(self.dc_image, (int(w*scale), int(h*scale)))
			self.dc_rect = self.dc_image.get_rect()
			self.dc_rect.center = (320,240)
			self.mode = 0
			self.troops = [20,15,15,15,10]

			# wait image
			self.wait_image = pygame.image.load("../media/wait_p1.png")
			w,h = self.wait_image.get_size()
			scale = .35
			self.wait_image = pygame.transform.scale(self.wait_image, (int(w*scale), int(h*scale)))
			self.wait_rect = self.wait_image.get_rect()
			self.wait_rect.center = (320,240)

			# win
			self.win_image = pygame.image.load("../media/win.png")
			w,h = self.win_image.get_size()
			scale = .8
			self.win_image = pygame.transform.scale(self.win_image, (int(w*scale), int(h*scale)))
			self.win_rect = self.win_image.get_rect()
			self.win_rect.center = (320,240)

			# lose
			self.lose_image = pygame.image.load("../media/lose.png")
			w,h = self.lose_image.get_size()
			scale = .8
			self.lose_image = pygame.transform.scale(self.lose_image, (int(w*scale), int(h*scale)))
			self.lose_rect = self.lose_image.get_rect()
			self.lose_rect.center = (320,240)

			# 2) set up game objects
			self.parachuters = []
			self.bullets = []
			self.gun = Gun(self)
			self.turret = Turret(self)

			self.trans_info = []
			self.out_of_troops = False

			# font for display
			self.font = pygame.font.Font(None,36)

	def game_loop_iterate(self):
			# calculate/set theta
			mx, my = pygame.mouse.get_pos()
			O = my - self.turret.rect.center[1]
			A = mx - self.turret.rect.center[0]
			self.theta = math.atan2(-O,float(A))
			if self.theta < 0 and self.theta > -math.pi/2:
				self.theta = 0
			elif self.theta < 0 and self.theta < -math.pi/2:
				self.theta = math.pi

			if sum(self.troops) == 0 and self.out_of_troops == False:
				self.out_of_troops = True
				self.trans_info.append("no more troops")

			# 5) user inputs
			self.clean_parachuters()
			self.clean_bullets()
			for event in pygame.event.get():
				if event.type == QUIT:
					reactor.stop()
				if self.conn_status == 1:
					if event.type == MOUSEBUTTONDOWN:
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
					
			# 6) send a tick to every game object
			if self.conn_status == 1:
				self.turret.tick()
				self.gun.tick()
				for parachuter in self.parachuters:
					parachuter.tick()
				for bullet in self.bullets:
					bullet.tick()

			# 6.5 update trans_info
			

			# 7) display the game objects
			self.screen.blit(self.bg,(0,0))
			for bullet in self.bullets:
				self.screen.blit(bullet.image,bullet.rect)
			self.screen.blit(self.gun.image, self.gun.rect)
			self.screen.blit(self.turret.image,self.turret.rect)
			for parachuter in self.parachuters:
			#	pygame.draw.rect(parachuter.image,(255,255,0),(parachuter.para_rect.left,parachuter.para_rect.top,parachuter.para_rect.width,parachuter.para_rect.height))
			#	pygame.draw.rect(parachuter.image,(255,255,0),(parachuter.body_rect.x,parachuter.body_rect.y,parachuter.body_rect.width,parachuter.body_rect.height))
				self.screen.blit(parachuter.image,parachuter.rect)
			troops_string = "Cyborgs: " + str(self.troops)
			text = self.font.render(troops_string,1,(255,255,255))
			textpos = text.get_rect()
			textpos.centerx = self.bg.get_rect().centerx
			self.screen.blit(text,textpos)
			if self.conn_status == 2:
				self.screen.blit(self.dc_image, self.dc_rect)
			if self.conn_status == 0:
				self.screen.blit(self.wait_image, self.wait_rect)
			if self.conn_status == 3:
				self.screen.blit(self.win_image, self.win_rect)
			if self.conn_status == 4:
				self.screen.blit(self.lose_image, self.lose_rect)
			pygame.display.flip()

	def update(self, trans_info):
		del self.parachuters[:]
		del self.bullets[:]
		self.parachuters = [Parachuter(parachuter,self) for parachuter in trans_info["parachuters"]]
		self.bullets = [Bullet((bullet[0].x, bullet[0].y), bullet[1], self) for bullet in trans_info["bullets"]]
		self.gun.rect = trans_info['gun'][0]
		self.gun.theta_d = trans_info['gun'][1]
		if trans_info['lost'] == 4:
			self.conn_status = 3
		if trans_info['lost'] == 3:
			self.conn_status = 4

	def clean_parachuters(self):
		self.parachuters = [value for value in self.parachuters if value.reached_bottom == False]
		self.parachuters = [value for value in self.parachuters if value.hit == False]
	def clean_bullets(self):
		self.bullets = [value for value in self.bullets if value.out_of_bounds == False]
		self.bullets = [value for value in self.bullets if value.hit == False]

if __name__ ==  '__main__':
	gs = GameSpace()
	gs.init()
	lc = LoopingCall(gs.game_loop_iterate)
	lc.start(1/60)
	reactor.connectTCP('10.18.73.190', 42668, ParaConnFactory(gs))
	reactor.run()
