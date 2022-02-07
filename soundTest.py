import pygame

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()

with open('./sounds/itemDropped.ogg') as soundFile:
    sound = pygame.mixer.Sound(file=soundFile)
    pygame.mixer.Channel(6).play(sound)

import time
time.sleep(5)
