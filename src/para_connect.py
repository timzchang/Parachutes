# Name: Christopher Syers, Tim Chang

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

class ParaConnection(Protocol):
	def __init__(self, addr, gs):
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		print "connection made"
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
		print "retry connection"
		ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, start_pos, theta,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/bullet.png")
		scale = 1
		w,h = self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.ypos =  start_pos[1]
		self.xpos =  start_pos[0]
		self.rect.center = (self.xpos,self.ypos)
		self.out_of_bounds = False
		self.theta = theta
		# self.xpos =  320 + 65 * math.cos(self.gs.theta)
		# self.xpos =  320 + 65 * math.cos(self.gs.theta)
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
		temp_center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image,self.theta_d + 200)

class Parachuter(pygame.sprite.Sprite):
	def __init__(self,parachuter_info,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.color = parachuter_info[2]
		self.image = pygame.image.load("../media/" + self.color +"parachute.png")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.para_rect = pygame.rect.Rect((0,0),(64,20))
		self.body_rect = pygame.rect.Rect((0,0),(17,25))
		self.rect.center = parachuter_info[0]
		self.para_rect.center = (self.rect.center[0], self.rect.center[1] - 16)
		self.body_rect.midbottom = (self.rect.midbottom[0] - 7, self.rect.midbottom[1])
		self.speed = 6
		self.dy = 1
		self.reached_bottom = False
		self.hit = False
		self.hitpoints = parachuter_info[3]
		self.counter = 0
		self.speed = parachuter_info[1]
		self.sway = parachuter_info[4]
		self.sway_count = parachuter_info[5]
		self.sway_dir = parachuter_info[6]
		
	def tick(self):
		self.counter += 1
		if self.counter == self.speed:
			if self.sway:
				if self.sway_dir == "left":
					self.sway_count += 1
					if self.sway_count == 50:
						self.sway_count = 0
						self.sway_dir = "right"
					self.rect = self.rect.move(-1,self.dy)
					self.para_rect = self.para_rect.move(-1,self.dy)
					self.body_rect = self.body_rect.move(-1,self.dy)
				else:
					self.sway_count += 1
					if self.sway_count == 50:
						self.sway_count = 0
						self.sway_dir = "left"
					self.rect = self.rect.move(1,self.dy)
					self.para_rect = self.para_rect.move(1,self.dy)
					self.body_rect = self.body_rect.move(1,self.dy)
			else:
				self.rect = self.rect.move(0,self.dy)
				self.para_rect = self.para_rect.move(0,self.dy)
				self.body_rect = self.body_rect.move(0,self.dy)
		if self.rect.center[1] >= 450:
			self.reached_bottom = True

		index = self.body_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:
			self.hitpoints -= 1
			if self.hitpoints == 0:
				self.hit = True
			self.gs.bullets[index].hit = True
		index = self.para_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:	
			self.hitpoints -= 1
			if self.hitpoints == 0:
				self.hit = True
			self.gs.bullets[index].hit = True

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
			self.troops = [10,10,10,10,10]

			# wait image
			self.wait_image = pygame.image.load("../media/wait_p1.png")
			w,h = self.wait_image.get_size()
			scale = .35
			self.wait_image = pygame.transform.scale(self.wait_image, (int(w*scale), int(h*scale)))
			self.wait_rect = self.wait_image.get_rect()
			self.wait_rect.center = (320,240)

			# 2) set up game objects
			self.parachuters = []
			self.bullets = []
			self.gun = Gun(self)
			self.turret = Turret(self)

			self.trans_info = []

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
								print "adding para"
								self.trans_info.append(((pygame.mouse.get_pos()[0],10),10,"",1,False,0,"left"))
						elif self.mode == 1:
							if self.troops[1] > 0:
								self.troops[1] -= 1
								self.trans_info.append(((pygame.mouse.get_pos()[0],10),7,"purple_",1,True,0,"left"))
						elif self.mode == 2:
							if self.troops[2] > 0:
								self.troops[2] -= 1
								self.trans_info.append(((pygame.mouse.get_pos()[0],10),2,"blue_",1,False,0,"left"))
						elif self.mode == 3:
							if self.troops[3] > 0:
								self.troops[3] -= 1
								self.trans_info.append(((pygame.mouse.get_pos()[0],10),5,"red_",1,True,0,"left"))
						elif self.mode == 4:
							if self.troops[4] > 0:
								self.troops[4] -= 1
								self.trans_info.append(((pygame.mouse.get_pos()[0],10),10,"green_",5,False,0,"left"))
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
			pygame.display.flip()

	def update(self, trans_info):
		del self.parachuters[:]
		del self.bullets[:]
		self.parachuters = [Parachuter(parachuter,self) for parachuter in trans_info["parachuters"]]
		self.bullets = [Bullet((bullet[0].x, bullet[0].y), bullet[1], self) for bullet in trans_info["bullets"]]
		self.gun.rect = trans_info['gun'][0]
		self.gun.theta_d = trans_info['gun'][1]

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
	reactor.connectTCP('localhost', 42668, ParaConnFactory(gs))
	reactor.run()
