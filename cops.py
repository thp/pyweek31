#!/usr/bin/env python3
"""Speed Limit -- PyWeek#31 'Cops' -- Thomas Perl <thp.io>"""
# Copyright (c) 2021-04-02 Thomas Perl <m@thp.io>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#
# Requires:
#  PyGame Zero ("python3 -m pip install pgzero")
#
# How To Run:
#  pgzrun cops.py
#
# Sound Credits:
#  https://freesound.org/people/Eponn/sounds/420356/
#  https://freesound.org/people/InspectorJ/sounds/448226/
#  https://freesound.org/people/shinephoenixstormcrow/sounds/337049/
#  https://freesound.org/people/egomassive/sounds/536769/
#
# Artwork:
#  Done by me in GIMP / VNC from a tablet
#
# Time spent:
#  ~ 4 hours in the afternoon of 2021-04-02
#

import random
import math
import pygame
import time

TITLE = __doc__
SCALING = 3
OWIDTH = 240
OHEIGHT = 136
WIDTH = OWIDTH * SCALING
HEIGHT = OHEIGHT * SCALING

class G:
    intro = True

    car = None

    speedlimit = random.choice([30, 50, 100])

    trash = []
    score = 0
    score_display = 0

    jitter = 0
    jitter_offset = 0

    history = ['indeterminate'] * 10
    history_index = 0
    history_wait = 0

def spawn_new_car():
    G.car = Actor(f'auto-{random.choice("abcd")}')
    G.car.wait = random.randint(10, 100)
    G.car.location = 0
    G.car.alocation = random.uniform(0.999, 1.01)
    G.car.dlocation = random.uniform(G.speedlimit * 0.5, G.speedlimit * 1.2)

spawn_new_car()

def scaled_draw():
    if G.intro:
        screen.blit('titlescreen', (0, 0))
        return

    screen.blit('background', (0, 0))
    screen.blit('policeman', (168, 54))
    screen.blit('radar', (155, 1))

    if G.car.wait:
        speedinfo = '---'
    else:
        speedinfo = f'{int(G.car.dlocation):03d}'
    for i, char in enumerate(speedinfo):
        screen.blit(f'digit-{char}', (189 + 8 * i, 8))

    screen.blit('score', (4, 5))
    for i, char in enumerate(f'{int(G.score_display):06d}'):
        screen.blit(f'scoredigit-{char}', (49 + 8 * i, 5))

    if not G.history_wait:
        screen.blit(f'signpost-{G.speedlimit}', (31, 42))

    for i, hist in enumerate(G.history):
        screen.blit(hist, (4 + 7 * i, 18))

    if not G.car.wait:
        G.car.draw()

    for trashcar in G.trash:
        trashcar.draw()

def draw():
    screen.fill((0, 0, 0))
    scaled_draw()

    surf = pygame.Surface((OWIDTH, OHEIGHT))
    if G.jitter_offset:
        for y in range(0, OHEIGHT, 2):
            xoff = G.jitter_offset + 2 * G.jitter_offset * math.sin((y+time.time())*1.4)
            surf.blit(screen.surface, (xoff, y), (0, y, OWIDTH, 2))
    else:
        surf.blit(screen.surface, (0, 0))
    #pygame.transform.scale2x(pygame.transform.scale2x(surf), screen.surface)
    pygame.transform.scale(surf, (WIDTH, HEIGHT), screen.surface)


def add_to_history(value):
    G.history[G.history_index] = value
    G.history_index += 1

    if G.history_index == len(G.history):
        G.history_wait = 100
        G.car.wait = 10000

def update():
    if G.intro:
        return

    if G.car.wait:
        G.car.wait -= 1
    else:
        if G.car.location < 50:
            G.car.dlocation *= G.car.alocation
        G.car.dlocation = max(20, G.car.dlocation)
        G.car.location += G.car.dlocation / 120

    if G.history_wait:
        G.history_wait -= 1
        if G.history_wait == 0:
            G.history = ['indeterminate'] * 10
            G.history_index = 0
            G.speedlimit = random.choice([30, 50, 100])
            spawn_new_car()

    G.score_display += (G.score - G.score_display) * 0.3
    if abs(G.score_display - G.score) < 2:
        G.score_display = G.score

    for trashcar in list(G.trash):
        if trashcar.right < 0:
            G.trash.remove(trashcar)

    for trashcar in G.trash:
        trashcar.angle += 2
        trashcar.x += trashcar.dx
        trashcar.dz += trashcar.az
        trashcar.z += trashcar.dz
        if trashcar.z < 0:
            sounds.hit.play()
            trashcar.z = 0
            trashcar.dz *= -0.9
        trashcar.y = trashcar.orig_y - trashcar.z

    if G.car.location >= 100:
        was_too_fast = (int(G.car.dlocation) > G.speedlimit)
        spawn_new_car()
        if was_too_fast:
            add_to_history('bad-nohit')
            sounds.escaping.play()
        else:
            add_to_history('good-nohit')
            sounds.ok.play()

    G.car.top = 151 * G.car.location / 100 - 14
    G.car.left = 130 - 102 * G.car.location / 100
    if G.jitter:
        G.jitter_offset = 30 * math.sin(2.2 * (10 - G.jitter)) * (1 - abs(G.jitter - 15) / 15)
        G.jitter -= 1
    else:
        G.jitter_offset = 0

def on_mouse_down(pos):
    if G.intro:
        G.intro = False
        return

    #G.jitter = 30

    pos = (pos[0] / SCALING, pos[1] / SCALING)
    if G.car.collidepoint(pos):
        was_too_fast = (int(G.car.dlocation) > G.speedlimit)
        score_multiplier = max(0, 100 - G.car.location) / 100

        trashcar = G.car
        spawn_new_car()

        trashcar.orig_y = trashcar.y
        trashcar.z = 0
        trashcar.dz = 10
        trashcar.az = -1
        trashcar.dx = -1.7
        G.trash.append(trashcar)

        if was_too_fast:
            G.score += 1000 * score_multiplier
            add_to_history('good-hit')
            sounds.ok.play()
        else:
            G.score = max(0, G.score - 5000)
            G.jitter = 30
            add_to_history('bad-hit')
            sounds.crash.play()

