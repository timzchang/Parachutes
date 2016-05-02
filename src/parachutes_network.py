# Name: Christopher Syers
# Date: April 15, 2016
# PyGame Primer

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

class Bullet(pygame.sprite.Sprite):
	def __init__(self,theta,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/bullet.png")
		scale = 1
		w,h = self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (300,430)
		self.out_of_bounds = False
		self.theta = theta
		self.xpos =  320 + 65 * math.cos(self.gs.theta)
		self.ypos =  435 - 65 * math.sin(self.gs.theta)
		self.hit = False

	def tick(self):
		self.xpos += 2*math.cos(self.theta)
		self.ypos -= 2* math.sin(self.theta)
		self.rect.center = (self.xpos,self.ypos)
		if self.rect.center[1] >= 480 or self.rect.center[1] <= 0 or self.rect.center[0] <= 0 or self.rect.center[0] >= 640:
			self.out_of_bounds = True

class Turret(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/turret_base.png")
		scale = .15
		w,h = self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (320,435)
		self.out_of_bound = False

	def tick(self):
		pass

class Gun(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/gun.png")
		scale = .15
		w,h =  self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (275, 400)
		self.orig_image = self.image
		self.radius = 50
		self.theta_d = 0

	def tick(self):
		self.theta_d = math.degrees(self.gs.theta)
		temp_center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, self.theta_d + 200)
		self.rect = self.image.get_rect()
		self.rect.center = (320+self.radius*math.cos(self.gs.theta),435-self.radius*math.sin(self.gs.theta))

class Parachuter(pygame.sprite.Sprite):
	def __init__(self,start_pos,speed,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/parachute.gif")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.para_rect = pygame.rect.Rect((0,0),(64,20))
		self.body_rect = pygame.rect.Rect((0,0),(17,25))
		self.rect.center = start_pos
		self.para_rect.center = (self.rect.center[0], self.rect.center[1] - 16)
		self.body_rect.midbottom = (self.rect.midbottom[0] - 7, self.rect.midbottom[1])
		self.dy = 1
		self.reached_bottom = False
		self.hit = False
		self.counter = 0
		self.speed = speed
		
	def tick(self):
		self.counter += 1
		if self.counter == self.speed:
			self.counter = 0
			self.rect = self.rect.move(0,self.dy)
			self.para_rect = self.para_rect.move(0,self.dy)
			self.body_rect = self.body_rect.move(0,self.dy)
		if self.rect.center[1] >= 450:
			self.reached_bottom = True

		index = self.body_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:
			self.gs.bullets[index].hit = True
			self.hit = True
		index = self.para_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:	
			self.gs.bullets[index].hit = True
			self.hit = True

class GameSpace:
	def init(self):
			# 1) basic initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)
			pygame.display.set_caption("Parachutes")
			self.bg = pygame.image.load("../media/background.png")
			self.bg = pygame.transform.scale(self.bg, (640,480))

			# 2) set up game objects
			self.parachuters = []
			self.bullets = []
			self.gun = Gun(self)
			self.turret = Turret(self)

			self.trans_info = {"bullets": [], "parachutes": []}
			self.client_events = []

	def game_loop_iterate(self):
			mx, my = pygame.mouse.get_pos()
			O = my - self.turret.rect.center[1]
			A = mx - self.turret.rect.center[0]
			self.theta = math.atan2(-O,float(A))
			if self.theta < 0 and self.theta > -math.pi/2:
				self.theta = 0
			elif self.theta < 0 and self.theta < -math.pi/2:
				self.theta = math.pi

			# 5) user inputs
			self.clean_parachuters()
			self.clean_bullets()
			for event in pygame.event.get():
				if event.type == QUIT:
					reactor.stop()
				if event.type == MOUSEBUTTONDOWN:
					#self.parachuters.append(Parachuter((mx, 10),1,self))
					self.bullets.append(Bullet(self.theta,self))
			for event in self.client_events:
					self.parachuters.append(Parachuter((event[0], 10),1,self))
			del self.client_events[:]
			# 6) send a tick to every game object
			self.turret.tick()
			self.gun.tick()
			for parachuter in self.parachuters:
				parachuter.tick()
			for bullet in self.bullets:
				bullet.tick()

			# 6.5 update trans_info
			self.trans_info['bullets'] = [(bullet.rect, bullet.theta) for bullet in self.bullets]
			self.trans_info['parachuters'] = [(parachuter.rect.center,parachuter.speed) for parachuter in self.parachuters]
			self.trans_info['gun'] = (self.gun.rect, self.gun.theta_d)

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
			pygame.display.flip()

	def clean_parachuters(self):
		self.parachuters = [value for value in self.parachuters if value.reached_bottom == False]
		self.parachuters = [value for value in self.parachuters if value.hit == False]
	def clean_bullets(self):
		self.bullets = [value for value in self.bullets if value.out_of_bounds == False]
		self.bullets = [value for value in self.bullets if value.hit == False]

class ParaConnection(Protocol):
	def __init__(self, addr, gs):
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		print "connection made to player 2"
		self.lc = LoopingCall(self.gs_pickler)
		self.lc.start(1/24)

	def gs_pickler(self):
		pv = pickle.dumps(self.gs.trans_info)
		pv = zlib.compress(pv)
		self.transport.write(pv)

	def dataReceived(self, data):
		pv = zlib.decompress(data)
		pv = pickle.loads(pv)
		self.gs.client_events = pv

	def connectionLost(self, reason):
		print "connection lost to player 2, ", reason
		self.lc.stop()

class ParaConnFactory(Factory):
	def __init__(self, gs):
		self.gs = gs

	def buildProtocol(self, addr):
		return ParaConnection(addr, self.gs)

if __name__ == '__main__':
	gs = GameSpace()
	gs.init()
	lc = LoopingCall(gs.game_loop_iterate)
	lc.start(1/60)
	reactor.listenTCP(42668,ParaConnFactory(gs))
	reactor.run()
	lc.stop()
