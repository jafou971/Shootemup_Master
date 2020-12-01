import pygame as pg
from math import atan2, pi, sin, cos
from random import random

class Entity:
    def __init__(self, pos: tuple, img_bnk: dict, act_img: str, creation_time: int = 0):
        self.x, self.y = pos
        self.img_bnk = img_bnk
        self.act_img = act_img
        self.body_angle = 0
        self.creation_time = creation_time
        self.alive = True

    @staticmethod
    def rotate(img: pg.Surface, angle: float = 0):
        center = img.get_rect().center
        rot_img = pg.transform.rotate(img, angle)
        new_rect = rot_img.get_rect(center = center)

        return rot_img, new_rect

    def animate(self, time: int):
        ...

    def show(self, s: pg.Surface, scale: float = 1):
        self.draw(s, None, self.body_angle, scale)

    def draw(self, s: pg.Surface, img_name: str = None, angle: float = 0, scale: float = 1) -> None:
        if img_name is None:
            img_name = self.act_img

        img = self.img_bnk[img_name]
        img = pg.transform.scale(img, [img.get_width() * scale, img.get_height() * scale])
        img, rect = Entity.rotate(img, angle)
        rect.x += self.x - 24 * scale
        rect.y += self.y - 24 * scale
        s.blit(img, rect)

    def move(self, x, y):
        self.x = x
        self.y = y


class Ship(Entity):
    def __init__(self, pos: tuple, img_bnk: dict):
        super(Ship, self).__init__(pos, img_bnk['player'], 'ship_0')
        self.level = 0
        self.level_frame = 0
        self.flame = 0
        self.flame_left = True
        self.flame_right = True
        self.body_angle = 0
        self.weapon_angle = 0
        self.dir = [0, -1]
        self.aim = [0, -100]
        self.vel = [0, 0]
        self.last_shot = 0
        self.life = 10


    def animate(self, time: int):
        if time % 3 == 0:
            if self.level_frame < self.level * 5:
                self.level_frame += 1

            self.flame += 1
            if self.flame > 4:
                self.flame = 0

        if time > 200 and time % 60 == 0 and self.level < 2:
            self.level += 1


    def show(self, s: pg.Surface, scale: float = 1):
        self.draw(s, 'ship_' + str(self.level_frame), self.body_angle, scale)
        self.draw(s, 'weapon_' + str(self.level_frame), self.weapon_angle, scale)

        if self.flame_right:
            self.draw(s, 'flame_R_' + str(self.level * 5 + self.flame), self.body_angle, scale)
        if self.flame_left:
            self.draw(s, 'flame_L_' + str(self.level * 5 + self.flame), self.body_angle, scale)


    def move(self, dx, dy):
        if dx or dy:
            n = 1.4 if (dx and dy) else 2
            self.dir = [n * dx, n * dy]

        self.flame_left = False
        self.flame_right = False

        angle =  atan2(self.dir[0], self.dir[1]) * 180 / pi - 180

        if abs(angle - self.body_angle) > 180:
            if self.body_angle > angle:
                self.body_angle -= 360
            else:
                self.body_angle += 360

        if self.level_frame == self.level * 5:
            if angle > self.body_angle:
                self.flame_right = True
                self.body_angle += 10
                self.weapon_angle += 10

            if angle < self.body_angle:
                self.flame_left = True
                self.body_angle -= 10
                self.weapon_angle -= 10

            if self.flame_left and self.flame_right:
                self.flame_left = False
                self.flame_right = False

            if (dx or dy) and abs(angle - self.body_angle) < 10:
                self.flame_left = True
                self.flame_right = True
                self.vel[0] += self.dir[0]
                self.vel[1] += self.dir[1]

        self.vel[0] *= 0.95
        self.vel[1] *= 0.95

        self.x += self.vel[0]
        self.y += self.vel[1]


    def aimTo(self, x, y):
        self.aim = [x - self.x, y - self.y]

        angle =  atan2(self.aim[0], self.aim[1]) * 180 / pi - 180

        if abs(angle - self.weapon_angle) > 180:
            if self.weapon_angle > angle:
                self.weapon_angle -= 360
            else:
                self.weapon_angle += 360

        if abs(angle - self.weapon_angle) < 9:
            self.weapon_angle = angle
        else:
            if angle > self.weapon_angle:
                self.weapon_angle += 9

            if angle < self.weapon_angle:
                self.weapon_angle -= 9


    def shoot(self, bullets: list, bank: dict, time: int):
        if time - self.last_shot > 12 / (self.level + 1):
            self.last_shot = time
            bullets.append(Bullet([self.x, self.y], [-sin(self.weapon_angle * pi / 180), -cos(self.weapon_angle * pi / 180)], bank, time))


class Enemy(Entity):
    def __init__(self, pos: tuple, img_bnk: dict, _type: str = "small", creation_time: int = 0):
        super(Enemy, self).__init__(pos, img_bnk[_type + '_enemy'], _type + '_enemy_0', creation_time)
        self.type = _type
        self.body_angle = 0
        self.anim_img = 0
        self.life = 3

    def animate(self, time: int):
        t = (time - self.creation_time)
        self.anim_img = (t // 10) % 4
        self.body_angle = -2 * t


    def show(self, s: pg.Surface, scale: float = 1):
        self.draw(s, f'enemy_{self.anim_img}', self.body_angle, scale)
        

    def move(self, time: int, W: int, H: int):
        t = (time - self.creation_time) / 30
        self.x = W / 2 + sin(t) * W / 3
        self.y = (H / 2) - (cos(t/5) * H * 0.6) + (cos(t * 3) * H / 15)


class Bullet(Entity):
    def __init__(self, pos: tuple, vel: tuple, bank: dict, creation_time: int = 0):
        super(Bullet, self).__init__(pos, bank['player'], 'bullet_0', creation_time)
        self.anim_img = 0
        self.vel = vel

        for i in range(3):
            self.move()
    

    def show(self, s: pg.Surface, scale: float = 1):
        self.draw(s, f'bullet_{self.anim_img}', self.body_angle, scale)


    def animate(self, time: int):
        t = (time - self.creation_time)
        self.anim_img = t % 4
        if t > 100:
            self.alive = False


    def move(self):
        self.x += self.vel[0] * 15
        self.y += self.vel[1] * 15

class Star:
    def __init__(self, W: int, H: int, scale: float):
        self.limits = W, H
        self.x = 0
        self.y = 0
        self.size = 1
        self.scale = scale
        self.rand_time = 0

    def rand(self):
        W, H = self.limits
        self.x = int(random() * W)
        self.y = int(random() * (H + 100)) - 100
        self.size = random() * self.scale * 1.2
        self.rand_time += random() * 100

    def move(self, time):
        self.y += self.size * 2
        if time > self.rand_time:
            self.rand()

    def show(self, s: pg.Surface):
        pg.draw.rect(s, [200, 200, 200], [self.x, self.y, self.size, self.size])
        