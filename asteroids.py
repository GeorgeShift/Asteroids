import pyglet
from pyglet import gl
from pyglet.window import key
import math

# Konstanty
SIRKA = 800
VYSKA = 600
RYCHLOST_OTACENI = 360
AKCELERACE = 200

# Globální proměnné
objekty = []  # globální seznam objektů
stisknute_klavesy = set()  # sada stisknutych klaves
batch = pyglet.graphics.Batch()  # kolekce s objekty pro vykreslení


class Spaceship:
    """ Třída reprezentující vesmírnou loď"""
    def __init__(self, x, y, soubor):
        # nastavení souradnic obrázku na střed hrací plochy
        self.x = x
        self.y = y
        self.rychlost = 0
        self.rotace = 0
        # načtení obrázku ze souboru
        obrazek = pyglet.image.load(soubor)
        # nastavní "kotvy" obrázku na střed
        obrazek.anchor_x = obrazek.width // 2
        obrazek.anchor_y = obrazek.height // 2
        self.sprite = pyglet.sprite.Sprite(
            obrazek, self.x,
            self.y, batch=batch)

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


def vykresli_scenu():
    window.clear()

    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)

            # Draw
            batch.draw()

            # Restore remembered state (this cancels the glTranslatef)
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


lod = Spaceship(SIRKA // 2, VYSKA // 2, 'ship.png')
objekty.append(lod)

pyglet.clock.schedule_interval(objekty[0].tick, 1/100)
window = pyglet.window.Window(width=SIRKA, height=VYSKA)

window.push_handlers(
    on_draw=vykresli_scenu,
    on_key_press=stisk_klavesy,
    on_key_release=pusteni_klavesy,
)
pyglet.app.run()  # vse je nastaveno, at zacne hra
