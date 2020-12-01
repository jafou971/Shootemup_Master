import pygame as pg
import os, platform,math
from entities import Entity, Ship, Star, Enemy
from random import random

def getImgDict(path: str) -> dict:
	d = {}
	for file in os.listdir(path):
		if '.' in file:
			name, ext = file.split('.')
			if ext in ['jpg', 'png']:
				d[name] = pg.image.load(path + '/' + file).convert_alpha()
		else:
			d[file] = getImgDict(path + '/' + file)
	return d

def drawText(surface: pg.surface, text: str, x: int, y: int, fontsize: int = 24, color: list = [255]*4, bold: bool = False, side: str = 'left') -> None:
	f = pg.font.Font('../Consolas.ttf', fontsize)
	f.set_bold(bold)
	t = f.render(text, False, color)
	w = t.get_size()[0]

	if side == 'left':
		surface.blit(t, [x, y])
		
	if side == 'center':
		surface.blit(t, [x - w // 2, y])
		
	if side == 'right':
		surface.blit(t, [x - w, y])

def randPos(W: int, H: int) -> tuple:
	return int(random() * W), int(random() * H)

if __name__ == "__main__":
	if 'Windows' in platform.platform():  # car pb de dpi sur windows
		from ctypes import windll
		windll.shcore.SetProcessDpiAwareness(1)

	pg.init()
	clock = pg.time.Clock()

	SCREEN_W, SCREEN_H = 1500, 900
	SCREEN = pg.display.set_mode((SCREEN_W, SCREEN_H))
	SCALE = 3

	images = getImgDict('../img')
	time = 0
	
	player = Ship([SCREEN_W // 2, SCREEN_H // 2], images)
	enemies = []
	bullets = []
	stars = [Star(SCREEN_W, SCREEN_H, SCALE) for i in range(100)]

	cursor = 0
	mode = 'menu'
	while mode:
		time += 1
		clock.tick(30)
		
		for e in pg.event.get():
			if e.type == pg.QUIT:
				mode = None
				continue

		keys_press = pg.key.get_pressed()
		mouse_press = pg.mouse.get_pressed()[0]
		mouse_pos = pg.mouse.get_pos()

		SCREEN.fill([0, 0, 0])

		for star in stars:
			star.move(time)
			star.show(SCREEN)

		direction = [0, 0]

		if mode == 'menu':
			if keys_press[pg.K_UP]: cursor = 0
			if keys_press[pg.K_DOWN]: cursor = 1

			drawText(SCREEN, 'Shoot Moop', SCREEN_W // 2, SCREEN_H // 4, 56, [255]*3, True, 'center')
			drawText(SCREEN, 'Play', SCREEN_W // 2, SCREEN_H * 3 // 4, 36, [128 if cursor else 255]*3, side = 'center')
			drawText(SCREEN, 'Quit', SCREEN_W // 2, SCREEN_H * 3 // 4 + 40, 36, [255 if cursor else 128]*3, side = 'center')


			if keys_press[pg.K_RETURN] or keys_press[pg.K_SPACE]:
				if cursor:
					mode = None
				else:
					mode = 'game'
			
		if mode == 'game':
			if keys_press[pg.K_ESCAPE] :
					mode = 'menu'

			if keys_press[pg.K_w]: direction[1] -= 1
			if keys_press[pg.K_s]: direction[1] += 1
			if keys_press[pg.K_a]: direction[0] -= 1
			if keys_press[pg.K_d]: direction[0] += 1

			player.aimTo(*mouse_pos)

			if mouse_press:
				player.shoot(bullets, images, time)

			if time % 50 == 0 and len(enemies) < 6:
				enemies.append(Enemy((SCREEN_W // 2, -50), images, creation_time = time))

			if time % 50 == 0:
				player.life -=50

			if player.life <= 0:
				mode = 'menu'

			

		temp = []
		for enemy in enemies:
			enemy.move(time, SCREEN_W, SCREEN_H)
			enemy.animate(time)
			enemy.show(SCREEN, SCALE)

			if (enemy.alive):
				temp.append(enemy)
		enemies = temp

		player.move(*direction)
		player.animate(time)
		player.show(SCREEN, SCALE)

		temp = []
		for bullet in bullets:
			bullet.move()
			bullet.animate(time)
			bullet.show(SCREEN, SCALE)


			if (bullet.alive):
				temp.append(bullet)
		bullets = temp


		
		pg.display.update()