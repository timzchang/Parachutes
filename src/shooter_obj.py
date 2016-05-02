import math
import os
import sys
import pygame
from pygame.locals import *

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
	def __init__(self,parachuter_info,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.color = parachuter_info[2]
		self.image = pygame.image.load("../media/" + self.color + "parachute.png")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.para_rect = pygame.rect.Rect((0,0),(64,20))
		self.body_rect = pygame.rect.Rect((0,0),(17,25))
		self.rect.center = parachuter_info[0]
		self.para_rect.center = (self.rect.center[0], self.rect.center[1] - 16)
		self.body_rect.midbottom = (self.rect.midbottom[0] - 7, self.rect.midbottom[1])
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
			self.counter = 0
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
