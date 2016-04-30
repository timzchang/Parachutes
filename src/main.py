# Name: Christopher Syers
# Date: April 15, 2016
# PyGame Primer

import math
import os
import sys
import pygame
from pygame.locals import *

class Laser(pygame.sprite.Sprite):
	def __init__(self,gs=None,theta=None,center=None):
		theta = theta + 45
		self.theta = math.radians(theta)
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("laser.png")
		self.rect = self.image.get_rect()

		self.xpos = center[0]+40*math.cos(self.theta)
		self.ypos = center[1]-40*math.sin(self.theta)
		self.rect.center = (self.xpos,self.ypos)

		self.damaged = False

	def tick(self):
		#self.rect = self.rect.move(5*math.cos(self.theta),-5*math.sin(self.theta))
		self.xpos += 5*math.cos(self.theta)
		self.ypos -= 5*math.sin(self.theta)
		self.rect.center = (self.xpos,self.ypos)

class Explosion(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.images = []
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames016a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames000a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames001a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames002a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames003a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames004a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames005a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames006a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames007a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames008a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames009a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames010a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames011a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames012a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames013a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames014a.png"),(400,400)))
		self.images.append(pygame.transform.scale(pygame.image.load("explosion/frames015a.png"),(400,400)))
		self.image_index = 0
		self.image = self.images[self.image_index]
		self.rect = self.image.get_rect()
		self.rect.center = (500,450)
		self.empty_image = pygame.image.load("empty.png")
		self.counter = 0
		self.gs.explosion_sound.play()

	def tick(self):
		self.counter += 1
		if self.counter == 7:
			self.counter = 0
			self.image_index += 1
			if self.image_index == 17:
				self.image = self.empty_image
				self.gs.explosion_sound.fadeout(1000)
			elif self.image_index <= 16:
				self.image = self.images[self.image_index]
		else:
			pass

class Earth(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("globe.png")
		self.red_image = pygame.image.load("globe_red100.png")
		self.rect = self.image.get_rect()
		self.rect.center = (640,480)
		self.hitpoints = 300
		self.empty_image = pygame.image.load("empty.png")
		self.exploded = False

	def tick(self):
		if self.hitpoints == 0:
			if self.exploded == False:
				self.notexploded = True
				self.image = self.empty_image
				self.gs.explosions.append(Explosion(self.gs))
		elif self.hitpoints < 0:
			pass
		elif self.hitpoints < 100:
			self.image = self.red_image
		for laser in self.gs.lasers:
			if math.sqrt((640-laser.rect.center[0])**2+(480-laser.rect.center[1])**2) < 205:
				if laser.damaged == False:
					laser.damaged = True
					self.hitpoints -= 1
					break
				else:
					continue


class Deathstar(pygame.sprite.Sprite):
	def __init__(self,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("deathstar.png")
		self.rect = self.image.get_rect()
		self.speed = 2
		# keep original to limit resize erros
		self.orig_image = self.image
		self.tofire = False

	def fire(self):
		self.gs.laser_sound.play(loops=-1)
		self.tofire = True

	def ceasefire(self):
		self.gs.laser_sound.stop()
		self.tofire = False

	def tick(self):
		if self.tofire == True:
			# code to emit a laster beam block
			self.gs.lasers.append(Laser(self.gs,self.theta,self.rect.center))
		else:
			# code to calculate the angle between my current direction and the mouse position
			mx, my = pygame.mouse.get_pos()
			O = my - self.rect.center[1]
			A = mx - self.rect.center[0]
			self.theta = math.degrees(math.atan2(-O,float(A))) - 45
			temp_center = self.rect.center
			self.image = pygame.transform.rotate(self.orig_image,self.theta)
			self.rect = self.image.get_rect()
			self.rect.center = temp_center
	
	def move(self,keycode):
		if self.tofire == False:
			if keycode == K_LEFT:
				self.rect = self.rect.move(-self.speed,0)
			elif keycode == K_RIGHT:
				self.rect = self.rect.move(self.speed,0)
			elif keycode == K_DOWN:
				self.rect = self.rect.move(0,self.speed)
			elif keycode == K_UP:
				self.rect = self.rect.move(0,-self.speed)
			else:
				pass

class GameSpace:
	def main(self):
			# 1) basic initalization
			pygame.init()
			pygame.mixer.init()
			pygame.mixer.set_reserved(1)
			self.explosion_sound = pygame.mixer.Sound("explode.wav")
			self.laser_sound = pygame.mixer.Sound("screammachine.wav")
			self.explosion_sound.set_volume(1)
			self.laser_sound.set_volume(.50)
			self.size = self.wifth, self.height = 640, 480
			self.black = 0,0,0
			self.screen = pygame.display.set_mode(self.size)

			self.clock = pygame.time.Clock()
			pygame.key.set_repeat(50,100)

			# 2) set up game objects
			self.explosions = []
			self.lasers = []
			self.deathstar = Deathstar(self)
			self.earth = Earth(self)

			# 3) start game loop
			while 1:
				
				# 4) clock tick regulation (framerate)
				self.clock.tick(60)

				# 5) user inputs
				for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit()
					if event.type == KEYDOWN:
						self.deathstar.move(event.key)
					if event.type == MOUSEBUTTONDOWN:
						self.deathstar.fire()
					if event.type == MOUSEBUTTONUP:
						self.deathstar.ceasefire()
				# 6) send a tick to every game object
				self.deathstar.tick()
				self.earth.tick()
				for explosion in self.explosions:
					explosion.tick()
				for laser in self.lasers:
					laser.tick()

				# 7) display the game objects
				self.screen.fill(self.black)
				for laser in self.lasers:
					self.screen.blit(laser.image,laser.rect)
				self.screen.blit(self.deathstar.image,self.deathstar.rect)
				self.screen.blit(self.earth.image,self.earth.rect)
				for explosion in self.explosions:
					self.screen.blit(explosion.image,explosion.rect)

				pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
