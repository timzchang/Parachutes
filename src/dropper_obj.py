"""
Name: Christopher Syers, Tim Chang
Date: May 2, 2016
CSE30332 Programming Paradigms Final Project

dropper_obj.py

Game objects for the dropper.py file. Contains:
	Bullet:		bullet that can shoot down parachuters
	Turret:		base of the turret that shoots down the parachuters
	Gun:		barrel of the turret
	Parachuter:	object that falls from the sky and gets shot down
"""

import math
import os
import sys
import pygame
from pygame.locals import *

class Bullet(pygame.sprite.Sprite):
	"""
	Bullet: class that represents a bullets object that flies across the screen.
	Defined by a starting position and an angle at which to travel. Derives from 
	pygame Sprite
	"""
	def __init__(self, start_pos, theta,gs=None):
		"""
		Bullet.__init__: initializer for Bullet object. Takes in a starting position in the form
		of a coordinate point (x,y), and an angle in radians, and the game space in which it lives
		"""
		pygame.sprite.Sprite.__init__(self)				# call constructor of Pygame sprite
		self.gs = gs									# store its game space
		self.image = pygame.image.load("../media/bullet.png")	# load the bullet image from the media file
		self.rect = self.image.get_rect()						# get the rect of the image
		# start the bullet at the start_pos provided
		self.ypos =  start_pos[1]
		self.xpos =  start_pos[0]
		# set the center of the rectangle to the position provided in constructor
		self.rect.center = (self.xpos,self.ypos)
		self.out_of_bounds = False		# flag for if the bullet is out of bounds
		self.theta = theta				# store the angle it travels at
		self.hit = False				# flag to say whether or not the bullet has hit something

	def tick(self):
		"""
		Bullet.tick: fuction to update the Bullet object
		Moves it and detects if it is out of bounds
		"""
		# move the position of the bullet
		self.xpos += 2*math.cos(self.theta)
		self.ypos -= 2* math.sin(self.theta)
		self.rect.center = (self.xpos,self.ypos)
		# if the bullet is beyond the boundary of the screen, set the flag
		if self.rect.center[1] >= 480 or self.rect.center[1] <= 0 or self.rect.center[0] <= 0 or self.rect.center[0] >= 640:
			self.out_of_bounds = True

class Turret(pygame.sprite.Sprite):
	"""
	Turret: class that is the base of the gun that shoots down the parachuters.
	"""
	def __init__(self,gs=None):
		"""
		Turret.__init__: initializer for the turret class. Sets the game space in which is lives
		and gives it an image and position. Derives from pygame Sprite
		"""
		pygame.sprite.Sprite.__init__(self)					# class constructor of pygame Sprite
		self.gs = gs										# store the game space in which it lives
		self.image = pygame.image.load("../media/turret_base.png")	# load the turret_base.png image from the media folder
		# scale the image size down to a better size
		scale = .15											
		w,h = self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		# set its center to the bottom middle of the screen
		self.rect.center = (320,435)

class Gun(pygame.sprite.Sprite):
	"""
	Gun: class for the gun part of the turret. Derives from pygame Sprite. Follows the mouse.
	"""
	def __init__(self, gs=None):
		"""
		Gun.__init__: initializer for the Gun class. Loads the image, scales it down, and positions it
		correctly in the gamesapce.
		"""
		pygame.sprite.Sprite.__init__(self)				# call constructor of pygame Sprite
		self.gs = gs									# store its game state
		self.image = pygame.image.load("../media/gun.png")	# load the image
		# scale the image down to a better size
		scale = .15				
		w,h =  self.image.get_size()
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		# set the center of the turret
		self.rect.center = (275, 400)
		self.orig_image = self.image	# store original image to apply the rotations to avoid degradation
		self.theta_d = 0				# member variable for the angle of the image
		# rotate the image so it starts in a natural position
		self.image = pygame.transform.rotate(self.orig_image,self.theta_d + 200)

	def tick(self):
		"""
		Gun.tick: function that updates the gun image based on the info in theta_d, which is changed in the 
		update function of the game space.
		"""
		self.image = pygame.transform.rotate(self.orig_image,self.theta_d + 200)

class Parachuter(pygame.sprite.Sprite):
	"""
	Parachuter: class for the parachuters that fall from the sky. There are many different stats that 
	control the appearance and behavior of the parachuters. This is passed into the constructor in 
	parachuter_info. A parachuter is defined by the following data members:
		parachuter_info[0] - center: position of the parachuter
		parachuter_info[1] - speed: how many ticks it takes for the parachuter to move, lower number is faster fall
		parachuter_info[2] - color: color of the parachuter loaded
		parachuter_info[3] - hitpoints: how many shots it takes to kill the parachuter
		parachuter_info[4] - sway: boolean that tells whether or not the parachuter sways
		parachuter_info[5] - sway_count: how many times a parachuter has gone left or right, goes up to 10
		parachuter_info[6] - sway_dir: "left" or "right", depending on which way the parachuter is swaying
	"""
	def __init__(self,parachuter_info,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.color = parachuter_info[2]			# color of the parachuters
		# load the image according to the color and scale it down to fit better
		self.image = pygame.image.load("../media/" + self.color +"parachute.png")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()

		# make smaller rectangle for the body and parachute portion of the image - used for collision detection
		self.para_rect = pygame.rect.Rect((0,0),(64,20))
		self.body_rect = pygame.rect.Rect((0,0),(17,25))

		# set the center of the parachuter to the info passed in, and set the center of the hitbox rectangles
		self.rect.center = parachuter_info[0]
		self.para_rect.center = (self.rect.center[0], self.rect.center[1] - 16)
		self.body_rect.midbottom = (self.rect.midbottom[0] - 7, self.rect.midbottom[1])

		# set various data members
		self.dy = 1						# how many pixels it goes down every time it moves
		self.reached_bottom = False		# boolean if it reached the bottom
		self.hit = False				# boolean to tell if it was hit by a bullet
		self.hitpoints = parachuter_info[3]	# set the number of hitpoints
		self.counter = 0					# a counter that counts how many ticks have gone by since a move
		self.speed = parachuter_info[1]		# how many ticks it takes to make a move
		self.sway = parachuter_info[4]		# boolean - does it sway or not?
		self.sway_count = parachuter_info[5]	# how many times it has gone left or right
		self.sway_dir = parachuter_info[6]	# "left" or "right", tell which way it goes when it sways
		
	def tick(self):
		"""
		Parachuter.tick: function to update the position and and info of a parachuter.
		"""
		self.counter += 1					# update the counter
		# if the counter is at the speed threshold
		if self.counter == self.speed:		
			# if it needs to sway
			if self.sway:
				# if it is going left
				if self.sway_dir == "left":
					self.sway_count += 1
					# if it has gone 50 pixels to the left, reset the count and set it to go right
					if self.sway_count == 50:
						self.sway_count = 0
						self.sway_dir = "right"
					# move the three rectangles over and down
					self.rect = self.rect.move(-1,self.dy)
					self.para_rect = self.para_rect.move(-1,self.dy)
					self.body_rect = self.body_rect.move(-1,self.dy)
				# if it is going right
				else:
					self.sway_count += 1
					# if it has gone 50 pixels to the right, reset the count and set it to go left
					if self.sway_count == 50:
						self.sway_count = 0
						self.sway_dir = "left"
					# move the three rectangles over and down
					self.rect = self.rect.move(1,self.dy)
					self.para_rect = self.para_rect.move(1,self.dy)
					self.body_rect = self.body_rect.move(1,self.dy)
			# if it does not sway, just move it down
			else:
				# move the three rectangles down
				self.rect = self.rect.move(0,self.dy)
				self.para_rect = self.para_rect.move(0,self.dy)
				self.body_rect = self.body_rect.move(0,self.dy)
		# if the parachuter is at the bottom, set the flag to true
		if self.rect.center[1] >= 450:
			self.reached_bottom = True

		# Collision detection between the bullets and the body_rect and para_rect
		index = self.body_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		# if there was a bullet that has not hit another parachuter that is hitting this parachuter in the body
		if index >= 0:
			# reduce the hitpoints
			self.hitpoints -= 1
			# if the hitpoints are below 0, indicate that the parachuter is dead
			if self.hitpoints == 0:
				self.hit = True
			# indicate that the bullet has hit something
			self.gs.bullets[index].hit = True


		index = self.para_rect.collidelist([bullet.rect for bullet in self.gs.bullets if bullet.hit == False])
		# if there was a bullet that has not hit another parachuter that is hitting this parachuter in the parachuter
		if index >= 0:	
			# reduce the hitpoints
			self.hitpoints -= 1
			# if the hitpoints are below 0, indicate that the parachuter is dead
			if self.hitpoints == 0:
				self.hit = True
			# indicate that the bullet has hit something
			self.gs.bullets[index].hit = True
