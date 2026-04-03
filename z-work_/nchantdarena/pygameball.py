#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 21:18:50 2019

@author: solubrew
"""

import pygame, time, random
print('Say something',pygame.__file__)
pygame.init()
dh = 1800
dw = 900
colors = {'black': [0,0,0], 'white':[255,255,255],
			'red': [255,0,0,]}
gameDisplay = pygame.display.set_mode((dh,dw))# create window
pygame.display.set_caption('')
clock = pygame.time.Clock()

carImg = pygame.image.load('assets/racecar.png')
roadImg = pygame.image.load('assets/road.png')
ballImg = pygame.image.load('assets/blueStone.png')
def thing(thgx, thgy, thgw, thgh, thgc):
	pygame.draw.rect(gameDisplay, thgc, [thgx, thgy, thgw, thgh])


def ball(x,y):
	gameDisplay.blit(ballImg, (x,y))
def car(x,y):
	gameDisplay.blit(carImg, (x,y))
carwidth = 25
carhieght = 25
def road(x, y):
	rw = 32
	rh = 32
	rx = x-rw/2
	ry = dw-rh
	for i in range(int(dh/rh)):
		gameDisplay.blit(roadImg, (rx,ry-rh*i))
def text_objects(text, font):
	textSurface = font.render(text, True, colors['red'])
	return textSurface, textSurface.get_rect()
def message_display(text):
	largeText = pygame.font.Font('freesansbold.ttf',115)
	TextSurf, TextRect = text_objects(text, largeText)
	TextRect.center = ((dw/2), (dh/2))
	gameDisplay.blit(TextSurf, TextRect)
	pygame.display.update()
	time.sleep(2)
	gameLoop()
def crash():
	message_display('You Crashed')
def gameLoop():
	x = dh*0.45
	y = dw*0.8
	xd = x
	yd = y
	x_delta = 0
	y_delta = -1


	thg_strty = -600
	thg_speed = 7
	thg_w = 100
	thg_h = 100

	gameExit = False
	while not gameExit:
		for event in pygame.event.get():#gets all events
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					x_delta = -1
				elif event.key == pygame.K_RIGHT:
					x_delta = 1
				elif event.key == pygame.K_DOWN:
					y_delta = 1
				elif event.key == pygame.K_UP:
					y_delta = -1
			if event.type == pygame.KEYUP:
				x_delta = 0
				y_delta = 0
			print(event)
		xd += x_delta
		yd += y_delta
		gameDisplay.fill(colors['white'])
		for b in range(random.randrange(0, 10)):
			thg_strtx = random.randrange(0, dw)
			thing(thg_strtx, thg_strty, thg_w, thg_h, colors['red'])
		thg_strty += thg_speed
		road(x,y)
		car(xd,yd)
		#ball(xd, yd)
		#creates a boundary in the x
		if xd > dw - carwidth or xd < 0:
			crash()
		pygame.display.update()
		clock.tick(60)
gameLoop()









