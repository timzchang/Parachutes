# Name: Christopher Syers, Tim Chang

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
from shooter_obj import *

class ParaConnection(Protocol):
	def __init__(self, addr, gs):
		self.addr = addr
		self.gs = gs

	def connectionMade(self):
		# print "connection made to player 2"
		self.lc = LoopingCall(self.gs_pickler)
		self.lc.start(1/24)
		self.gs.conn_status = 1

	def gs_pickler(self):
		pv = pickle.dumps(self.gs.trans_info)
		pv = zlib.compress(pv)
		self.transport.write(pv)

	def dataReceived(self, data):
		pv = zlib.decompress(data)
		pv = pickle.loads(pv)
		self.gs.client_events = pv

	def connectionLost(self, reason):
		# print "connection lost to player 2, ", reason
		self.gs.conn_status = 2
		self.lc.stop()

class ParaConnFactory(Factory):
	def __init__(self, gs):
		self.gs = gs

	def buildProtocol(self, addr):
		return ParaConnection(addr, self.gs)

class GameSpace:
	def init(self):
			# 1) basic initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)
			pygame.display.set_caption("Parachutes")
			self.bg = pygame.image.load("../media/background.png")
			self.bg = pygame.transform.scale(self.bg, (640,480))

			# dc image
			self.dc_image = pygame.image.load("../media/dc.png")
			w,h = self.dc_image.get_size()
			scale = .45
			self.dc_image = pygame.transform.scale(self.dc_image, (int(w*scale), int(h*scale)))
			self.dc_rect = self.dc_image.get_rect()
			self.dc_rect.center = (320,240)
			
			# wait image
			self.wait_image = pygame.image.load("../media/wait_p2.png")
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

			self.turret_lives = 5
			# 0 = waiting
			# 1 = playing
			# 2 = DC
			self.conn_status = 0

			# 2) set up game objects
			self.parachuters = []
			self.bullets = []
			self.gun = Gun(self)
			self.turret = Turret(self)

			self.trans_info = {"bullets": [], "parachutes": []}
			self.client_events = []
			self.dropper_out_of_troops = False

			self.font = pygame.font.Font(None,36)

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
			# set flag to end game when the turret is out of lives
			if self.turret_lives < 0:
				self.conn_status = 4

			for event in pygame.event.get():
				if event.type == QUIT:
					reactor.stop()
				if self.conn_status == 1:
					if event.type == MOUSEBUTTONDOWN:
						#self.parachuters.append(Parachuter((mx, 10),1,self))
						self.bullets.append(Bullet(self.theta,self))
			# 6) send a tick to every game object
			if self.conn_status == 1:
				for event in self.client_events:
						if event == "no more troops":
							self.dropper_out_of_troops = True
						else:
							self.parachuters.append(Parachuter(event,self))
				del self.client_events[:]
				self.turret.tick()
				self.gun.tick()
				for parachuter in self.parachuters:
					parachuter.tick()
				for bullet in self.bullets:
					bullet.tick()

			# 6.5 update trans_info
			self.trans_info['bullets'] = [(bullet.rect, bullet.theta) for bullet in self.bullets]
			self.trans_info['parachuters'] = [(parachuter.rect.center,parachuter.speed,parachuter.color,parachuter.hitpoints,parachuter.sway,parachuter.sway_count,parachuter.sway_dir) for parachuter in self.parachuters]
			self.trans_info['gun'] = (self.gun.rect, self.gun.theta_d)
			self.trans_info['lost'] = self.conn_status

			if self.dropper_out_of_troops and not self.parachuters:
				self.conn_status = 3

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
			if self.conn_status == 4:
				lives_string = "Lives: 0"
			else:
				lives_string = "Lives: " + str(self.turret_lives)
			text = self.font.render(lives_string,1,(255,255,255))
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


	def clean_parachuters(self):
		pre_clean = len(self.parachuters)
		self.parachuters = [value for value in self.parachuters if value.reached_bottom == False]
		post_clean = len(self.parachuters)
		self.turret_lives -= pre_clean - post_clean
		self.parachuters = [value for value in self.parachuters if value.hit == False]
	def clean_bullets(self):
		self.bullets = [value for value in self.bullets if value.out_of_bounds == False]
		self.bullets = [value for value in self.bullets if value.hit == False]


if __name__ == '__main__':
	gs = GameSpace()
	gs.init()
	lc = LoopingCall(gs.game_loop_iterate)
	lc.start(1/60)
	reactor.listenTCP(42668,ParaConnFactory(gs))
	reactor.run()
	lc.stop()
