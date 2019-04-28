import pyglet
from pyglet import gl
from pyglet.window import key
import math
import random
from random import randrange
import os

# konstanty
SIRKA = 800
VYSKA = 600
RYCHLOST_OTACENI = 360  # stupně/s
AKCELERACE = 200  # pixely/s

# obrázky objektů
obrazek_lodi = 'ship.png'
asteroidy_slozka = 'Meteors\\'
asteroidy = []

# globální proměnné
lode = []  # seznam lodí
objekty = []  # seznam dalších objektů
stisknute_klavesy = set()  # sada stisknutych klaves

batch = pyglet.graphics.Batch()  # kolekce s objekty pro vykreslení


class VesmirnyObjekt:
    """ Nadtřída reprezentující vesmírný objekt"""
    def __init__(self, obrazek):
        # načtení obrázku ze souboru
        obrazek = pyglet.image.load(obrazek)
        # nastavní "kotvy" obrázku na střed
        obrazek.anchor_x = obrazek.width // 2
        obrazek.anchor_y = obrazek.height // 2
        # výpočet poloměru objektu
        self.radius = (obrazek.width + obrazek.height) // 4
        self.sprite = pyglet.sprite.Sprite(
            obrazek, self.x,
            self.y, batch=batch)

    def delete(self, lod):
        lode[0].sprite.delete()
        lode.remove(lod)

    def tick(self, dt):
        rotace_rad = math.radians(-self.sprite.rotation + 90)
        self.x += self.rychlost * dt * math.cos(rotace_rad)
        self.y += self.rychlost * dt * math.sin(rotace_rad)
        # ošetření úniku raketky mimo hrací plochu
        if self.x > SIRKA:
            self.x -= SIRKA
        if self.x < 0:
            self.x += SIRKA
        if self.y > VYSKA:
            self.y -= VYSKA
        if self.y < 0:
            self.y += VYSKA
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = self.rotace


class Asteroid(VesmirnyObjekt):
    """ Třída reprezentující asteroid"""
    def __init__(self):
        self.rychlost = randrange(0, 200)
        self.rotace = randrange(0, 360)
        if randrange(0, 2):
            self.x = randrange(0, SIRKA)
            self.y = 0
        else:
            self.x = 0
            self.y = randrange(0, VYSKA)
        # výběr náhodného obrázku ze seznamu
        super().__init__(random.choice(asteroidy))

    def tick(self, dt):
        if len(lode) > 0:
            # Zjištění zda došlo ke kolizi
            for lod in lode:
                vzdalenost_x = abs(self.x - lod.x)
                vzdalenost_y = abs(self.y - lod.y)
                vzdalenost = math.sqrt(vzdalenost_x**2 + vzdalenost_y**2)
                if vzdalenost < abs(self.radius + lod.radius):
                    self.srazka_s_lodi(lod)
        super().tick(dt)

    def srazka_s_lodi(self, lod):
        self.delete(lod)


class VesmirnaLod(VesmirnyObjekt):
    """ Třída reprezentující vesmírnou loď"""
    def __init__(self):
        obrazek = obrazek_lodi
        self.rychlost = 0
        self.rotace = 0
        # nastavení souradnic obrázku na střed hrací plochy
        self.x = SIRKA // 2
        self.y = VYSKA // 2
        super().__init__(obrazek)

    # obsluha posouvání, natáčení a ovládání raketky
    def tick(self, dt):
        if 'nahoru' in stisknute_klavesy:
            self.rychlost += dt * AKCELERACE
        if 'dolu' in stisknute_klavesy:
            self.rychlost -= dt * AKCELERACE
            if self.rychlost < 0:
                self.rychlost = 0
        if 'doleva' in stisknute_klavesy:
            self.rotace -= RYCHLOST_OTACENI * dt
        if 'doprava' in stisknute_klavesy:
            self.rotace += RYCHLOST_OTACENI * dt
        super().tick(dt)


def vykresli_scenu():
    window.clear()

    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            gl.glPushMatrix()
            gl.glTranslatef(x_offset, y_offset, 0)
            batch.draw()
            gl.glPopMatrix()


def stisk_klavesy(symbol, modifikatory):
    if symbol == key.UP:
        stisknute_klavesy.add('nahoru')
    if symbol == key.DOWN:
        stisknute_klavesy.add('dolu')
    if symbol == key.LEFT:
        stisknute_klavesy.add('doleva')
    if symbol == key.RIGHT:
        stisknute_klavesy.add('doprava')


def pusteni_klavesy(symbol, modifikatory):
    if symbol == key.UP:
        stisknute_klavesy.discard('nahoru')
    if symbol == key.DOWN:
        stisknute_klavesy.discard('dolu')
    if symbol == key.LEFT:
        stisknute_klavesy.discard('doleva')
    if symbol == key.RIGHT:
        stisknute_klavesy.discard('doprava')


def obnov_stav(dt):
    for objekt in lode:
        objekt.tick(dt)
    for objekt in objekty:
        objekt.tick(dt)


# načtení všech asteroidů z adresáře do seznamu
# r=root, d=directories, f = files
for r, d, f in os.walk(asteroidy_slozka):
    for file in f:
        asteroidy.append(os.path.join(r, file))

# přidání vesmírné lodi do hracího pole
lod1 = VesmirnaLod()
lode.append(lod1)
# přidání asteroidů do hracího pole
for i in range(5):
    objekty.append(Asteroid())

pyglet.clock.schedule_interval(obnov_stav, 1/100)
window = pyglet.window.Window(width=SIRKA, height=VYSKA)

window.push_handlers(
    on_draw=vykresli_scenu,
    on_key_press=stisk_klavesy,
    on_key_release=pusteni_klavesy,
)
pyglet.app.run()  # vse je nastaveno, at zacne hra
