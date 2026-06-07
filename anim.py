from pyray import *
from settings import *

from enum import IntEnum

class AnimationType(IntEnum):
    REPEATING = 1
    ONESHOT = 2

class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1
#USED FROM IN CLASS ACTIVITY
class Animation:
    def __init__(self, first, last, cur, step, duration, duration_left, anim_type, row, sprites_in_row):
        self.first = first
        self.last = last
        self.cur = cur
        self.step = step
        self.duration = duration
        self.duration_left = duration_left
        self.type = anim_type
        self.row = row
        self.sprites_in_row = sprites_in_row 
        self.done = False

    def update(self, dt):
        self.duration_left -= dt
        
        if (self.duration_left<=0):
            self.duration_left = self.duration
            self.cur += self.step

            if (self.cur > self.last):
                match(self.type):
                    case AnimationType.ONESHOT:
                        self.cur = self.last 
                        self.done = True
                    case AnimationType.REPEATING:
                        self.cur = self.first 

    def frame(self, row):  # FIXES happened there to generalize to sprite sheet
        x = (self.cur % self.sprites_in_row) * SPRITE_SHEET_TILE_SIZE
        y =  SPRITE_SHEET_TILE_SIZE * self.row
        if row == 4:
            return Rectangle(x*2, y, SPRITE_SHEET_TILE_SIZE*2, SPRITE_SHEET_TILE_SIZE)


        return Rectangle(x, y, SPRITE_SHEET_TILE_SIZE, SPRITE_SHEET_TILE_SIZE)

    def reset(self): # ADDED
        self.cur = self.first
        self.done = False
        self.type = AnimationType.REPEATING
    
    #used for shoot animation, because shoot still exists but we need to reset the animation from last time
    def reset_oneshot(self): 
        self.cur = self.first
        self.done = False
        self.duration_left = self.duration