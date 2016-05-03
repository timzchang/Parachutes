"""
Name: Christopher Syers, Tim Chang
Date: May 2, 2016
CSE30332 Programming Paradigms Final Project

shooter_obj.py

Game objects for the dropper.py file. Contains:
	Bullet:		bullet that can shoot down parachuters
	Turret:		base of the turret that shoots down the parachuters
	Gun:		barrel of the turret
	Parachuter:	object that falls from the sky and gets shot down
"""
import math
import random
import os
import sys
import pygame
from pygame.locals import *

class Bullet(pygame.sprite.Sprite):
	"""Bullet: a bullet shot by Gun"""
	def __init__(self,theta,gs=None):
		"""__init__: load images/rects and initial positions
			based on angle of mouse to center of turret"""
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/bullet.png")
		scale = 1
		w,h = self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (300,430)
		self.theta = theta
		self.xpos =  320 + 65 * math.cos(self.gs.theta)
		self.ypos =  435 - 65 * math.sin(self.gs.theta)
		self.out_of_bounds = False
		self.hit = False

	def tick(self):
		"""tick: update the x/y position of the bullet"""
		self.xpos += 2*math.cos(self.theta)
		self.ypos -= 2* math.sin(self.theta)
		self.rect.center = (self.xpos,self.ypos)
		if self.rect.center[1] >= 480 or self.rect.center[1] <= 0 or self.rect.center[0] <= 0 or self.rect.center[0] >= 640:
			self.out_of_bounds = True

class Turret(pygame.sprite.Sprite):
	"""Turret: The base of the turret on the bottom of screen.
		It doesn't do much"""
	def __init__(self,gs=None):
		"""__init__: load and scale image"""
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
	"""Gun: The barrel of the turret. It follows the mouse and rotates
		around the center of the turret base."""
	def __init__(self, gs=None):
		"""__init__: loads images of Gun, sets a center, radius, 
			and initial angle"""
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/gun.png")
		scale = .15
		w,h =  self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = (275, 400)
		self.orig_image = self.image
		self.radius = 50  # distance from gun to center of turret base
		self.theta_d = 0

	def tick(self):
		"""tick: updates the position/rotation of the barrel"""
		self.theta_d = math.degrees(self.gs.theta)
		temp_center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, self.theta_d + 200)
		self.rect = self.image.get_rect()
		self.rect.center = (320+self.radius*math.cos(self.gs.theta),435-self.radius*math.sin(self.gs.theta))

class Parachuter(pygame.sprite.Sprite):
	"""Parachuter: aka the Cyborg. Main weapon of the dropper.
		Cyborgs come in 5 varieties:
			1. normal. 2 health. normal speed
			2. teleporter. 2 health. teleports on hit
			3. speedster. 2 health. goes 3 times as fast as normal
			4. swayer. 2 health. Sways back and forth
			5. tank. 7 health. Moves slower, but has 7 freaking health"""
	def __init__(self,parachuter_info,gs=None):
		"""__init__: initialize specific parachuters based on 
			info received via parachuter_info"""
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		# color of parachuter
		self.color = parachuter_info[2]
		self.image = pygame.image.load("../media/" + self.color + "parachute.png")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()

		# several hitboxes
		self.para_rect = pygame.rect.Rect((0,0),(64,20))
		self.body_rect = pygame.rect.Rect((0,0),(17,25))

		# set center
		self.rect.center = parachuter_info[0]
		self.para_rect.center = (self.rect.center[0], self.rect.center[1] - 16)
		self.body_rect.midbottom = (self.rect.midbottom[0] - 7, self.rect.midbottom[1])

		# status
		self.dy = 1
		self.reached_bottom = False
		self.hit = False

		# personal stats
		self.hitpoints = parachuter_info[3]
		self.counter = 0
		self.speed = parachuter_info[1]
		self.sway = parachuter_info[4]
		self.sway_count = parachuter_info[5]
		self.sway_dir = parachuter_info[6]

	def tick(self):
		"""tick: moves the parachuter, detects collisions
			with pesky bullets"""
		# only move once every few ticks
		self.counter += 1
		if self.counter == self.speed:
			self.counter = 0
			if self.sway:  # if sway then sway
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
			else:  # else move down
				self.rect = self.rect.move(0,self.dy)
				self.para_rect = self.para_rect.move(0,self.dy)
				self.body_rect = self.body_rect.move(0,self.dy)
		
		# reached bottom
		if self.rect.center[1] >= 450:
			self.reached_bottom = True

		# collision detection on body hitbox
		index = self.body_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:
			self.hitpoints -= 1
			if self.hitpoints > 0:
				if self.color == "purple_":  # if you purple, set a random new point
					rand = 40+random.random()*600
					self.rect.center = (rand,self.rect.center[1])
					self.body_rect.center = (rand,self.body_rect.center[1])
					self.para_rect.center = (rand,self.para_rect.center[1])
			if self.hitpoints == 0:  # ready to be cleaned next round
				self.hit = True
			self.gs.bullets[index].hit = True

		# collision detection on parachute hitbox
		index = self.para_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		if index >= 0:	
			self.hitpoints -= 1
			if self.hitpoints > 0:
				if self.color == "purple_":
					rand = 40+random.random()*600
					self.rect.center = (rand,self.rect.center[1])
					self.body_rect.center = (rand,self.body_rect.center[1])
					self.para_rect.center = (rand,self.para_rect.center[1])
			if self.hitpoints == 0:
				self.hit = True
			self.gs.bullets[index].hit = True
