import pygame

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()

sound = pygame.mixer.Sound('./sounds/itemDropped.ogg')
pygame.mixer.Channel(6).play(sound)

import time
time.sleep(5)
