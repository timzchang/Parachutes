# Name: Christopher Syers
# Date: April 15, 2016
# PyGame Primer

import math
import os
import sys
import pygame
from pygame.locals import *

class Parachuter(pygame.sprite.Sprite):
	def __init__(self,start_pos,gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("../media/parachute.gif")
		w,h = self.image.get_size()
		scale = .5
		self.image = pygame.transform.scale(self.image, (int(w*scale), int(h*scale)))
		self.rect = self.image.get_rect()
		self.rect.center = start_pos
		self.speed = 2
		
		
	def tick(self):
		self.rect = self.rect.move(0,self.speed)

class GameSpace:
	def main(self):
			# 1) basic initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)

			self.bg = pygame.image.load("../media/background.png")
			self.bg = pygame.transform.scale(self.bg, (640,480))
			self.clock = pygame.time.Clock()

			# 2) set up game objects
			self.parachuters = []
			# 3) start game loop
			while 1:
				
				# 4) clock tick regulation (framerate)
				self.clock.tick(60)

				# 5) user inputs
				for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit()
					if event.type == MOUSEBUTTONDOWN:
						self.parachuters.append(Parachuter(pygame.mouse.get_pos(),self))
						
				# 6) send a tick to every game object
				for parachuter in self.parachuters:
					parachuter.tick()

				# 7) display the game objects
				self.screen.blit(self.bg,(0,0))
				for parachuter in self.parachuters:
					self.screen.blit(parachuter.image,parachuter.rect)
				pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
