from enum import IntEnum


class PLAYER_STATE(IntEnum):
    IDLE = 3
    WALKING = 2
    SHOOTING = 0
    DODGING = 10
    DYING = 1
    DEAD = 20
class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1
class GAME_STATE(IntEnum):
    SPLASH = 0
    GAME_OVER = 1
    WIN = 2
    PLAYING = 3
    INSTRUCTIONS_FROM_SPLASH_SCREEN = 4
    INSTRUCTIONS_FROM_PAUSE_SCREEN = 5
    PAUSED = 6
    
