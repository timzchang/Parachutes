# Name: Christopher Syers
# Date: April 15, 2016
# PyGame Primer

import math
import os
import sys
import pygame
from pygame.locals import *


class GameSpace:
	def main(self):
			# 1) basic initalization
			pygame.init()
			self.size = self.wifth, self.height = 640, 480
			self.screen = pygame.display.set_mode(self.size)

			self.bg = pygame.image.load("../media/sky.png")
			self.clock = pygame.time.Clock()
			pygame.key.set_repeat(50,100)

			# 2) set up game objects

			# 3) start game loop
			while 1:
				
				# 4) clock tick regulation (framerate)
				self.clock.tick(60)

				# 5) user inputs
				for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit()

				# 6) send a tick to every game object

				# 7) display the game objects
				self.screen.blit(self.bg,(0,0))

				pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
