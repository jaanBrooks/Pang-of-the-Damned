
from pyray import *
from raylib import *
from random import randint, uniform
from os.path import join
from settings import *
from pang import *
from anim import *
from game_enums import *

class Player:
    
    def __init__(self):
        
        self.pos = Vector2(WINDOW_WIDTH/2, PLAYER_STARTING_Y)
        self.velocity = Vector2(0,0)
        self.score = 0
        self.anim_state = Animation(
            first=0, last=3, cur=0,
            step=1, duration = IDLE_DUR, duration_left=IDLE_DUR,
            anim_type=AnimationType.REPEATING,
            row=PLAYER_STATE.IDLE, sprites_in_row=4
        )
        
        self.normal_texture = load_texture(join('assets', 'skeleton_player.png'))
        self.dodge_texture = load_texture(join('assets', 'skeleton_dodge.png'))
        self.player_texture = self.normal_texture
        self.player_frame = self.anim_state.frame(self.anim_state.row)
        
        self.direction = Direction.RIGHT
        
        self.destination_rectangle = Rectangle(self.pos.x, self.pos.y, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE)
        self.collision_rectangle = Rectangle(self.pos.x + SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_WIDTH_RATIO, self.pos.y + SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_HEIGHT_RATIO, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_WIDTH_RATIO, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_HEIGHT_RATIO)
        
        self.trigger_shoot = False
        self.shooting_vertical = True
        
        self.dodge_cloud = Dodge_Cloud()
        
        self.shooting_cooldown = SHOOT_COOLDOWN
        self.dashing_cooldown = DODGE_COOLDOWN
        self.shooting_cooldown_left = 0
        self.dashing_cooldown_left = 0
        
    def startup(self):    
        
        self.dodge_cloud.startup()
        
        self.dash_icon_texture = load_texture(join('assets', 'dash_icon.png'))
        self.attack_icon_texture = load_texture(join('assets', 'attack_icon.png'))
        self.death_sound = load_sound(join("sound_effects", "death_sound_effect.mp3"))
        self.shooting_sound_effect = load_sound(join("sound_effects", "shooting_sound_effect.mp3"))
        self.dodge_sound_effect = load_sound(join("sound_effects", "dodge_sound_effect.mp3"))
        self.right_arrow_texture = load_texture(join('assets', 'sideways.png'))
        self.up_arrow_texture = load_texture(join('assets', 'up.png'))
    
    def reset(self):
        self.pos = Vector2(WINDOW_WIDTH/2, PLAYER_STARTING_Y)
        self.velocity = Vector2(0,0)
        self.score = 0
        self.anim_state = Animation(
            first=0, last=3, cur=0,
            step=1, duration = IDLE_DUR, duration_left=IDLE_DUR,
            anim_type=AnimationType.REPEATING,
            row=PLAYER_STATE.IDLE, sprites_in_row=4
        )
        self.direction = Direction.RIGHT
        self.destination_rectangle = Rectangle(self.pos.x, self.pos.y, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE)
        self.collision_rectangle = Rectangle(self.pos.x + SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_WIDTH_RATIO, self.pos.y + SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_HEIGHT_RATIO, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_WIDTH_RATIO, SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_HEIGHT_RATIO)
        self.trigger_shoot = False
        self.shooting_vertical = True
        self.shooting_cooldown = SHOOT_COOLDOWN
        self.dashing_cooldown = DODGE_COOLDOWN
        self.shooting_cooldown_left = 0
        self.dashing_cooldown_left = 0
   
    def transition(self, state):
        
        if state == self.anim_state.row:
            return
        self.anim_state.cur = 0
        
        match state:
            
            case PLAYER_STATE.IDLE:
                self.anim_state.row = PLAYER_STATE.IDLE
                self.anim_state.sprites_in_row = 4
                self.anim_state.duration = IDLE_DUR
            
            case PLAYER_STATE.WALKING:
                self.anim_state.row = PLAYER_STATE.WALKING
                self.anim_state.sprites_in_row = 12
                self.anim_state.duration = WALK_DUR
            
            case PLAYER_STATE.DODGING:
                play_sound(self.dodge_sound_effect)
                
                self.dodge_cloud.position.x = self.pos.x + (SPRITE_SHEET_TILE_SIZE /2 )
                self.dodge_cloud.position.y = self.pos.y + (SPRITE_SHEET_TILE_SIZE /2 )
                
                self.dodge_cloud.anim_state.reset_oneshot()
                self.dodge_cloud.active = True
                
                self.anim_state.duration = DODGE_DUR
                self.anim_state.duration_left = DODGE_DUR
                
                self.anim_state.type = AnimationType.ONESHOT
                self.anim_state.row = PLAYER_STATE.DODGING
                self.anim_state.sprites_in_row = 12
                
                
            case PLAYER_STATE.SHOOTING:
                play_sound(self.shooting_sound_effect)
                
                self.anim_state.row = PLAYER_STATE.SHOOTING
                self.anim_state.duration = SHOOT_ANIM_DUR
                self.anim_state.sprites_in_row = 13
                self.anim_state.type = AnimationType.ONESHOT
            
            case PLAYER_STATE.DYING:
                play_sound(self.death_sound)
                
                self.anim_state.row = PLAYER_STATE.DYING
                self.anim_state.sprites_in_row = 13
                self.anim_state.type = AnimationType.ONESHOT
                self.anim_state.duration = DYING_DUR
        
        self.anim_state.last = self.anim_state.sprites_in_row - 1
    
    def update(self, frame_time):
        
        self.dodge_cloud.update(frame_time)
        self.manage_cooldowns(frame_time)
        
        self.velocity = Vector2(0,0)
        
        if is_mouse_button_pressed(MOUSE_BUTTON_RIGHT): #doesn't matter what state player is in, should always be able to switch
            self.shooting_vertical = not self.shooting_vertical
        
        #update state machine
        match self.anim_state.row:
            
            case PLAYER_STATE.IDLE:
                
                if is_key_pressed(KEY_SPACE) and self.dashing_cooldown_left <= 0:
                    self.transition(PLAYER_STATE.DODGING)
                
                elif is_key_down(KEY_A):
                    self.move_left()
                
                elif is_key_down(KEY_D):
                    self.move_right()
                
                elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self.shooting_cooldown_left <= 0:
                    self.shoot()
            
            case PLAYER_STATE.WALKING:
                
                if is_key_pressed(KEY_SPACE) and self.dashing_cooldown_left <= 0:
                    self.transition(PLAYER_STATE.DODGING)
                
                elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self.shooting_cooldown_left <= 0:
                    self.shoot()
                
                elif is_key_down(KEY_A):
                    self.move_left()
                
                elif is_key_down(KEY_D):
                    self.move_right()
                
                else:
                    self.transition(PLAYER_STATE.IDLE)
            
            case PLAYER_STATE.DODGING:
                
                self.dodge()
                
                if self.anim_state.done:
                    self.dodge_cloud.position = Vector2(-100,-100) #necessary to prevent weird animation bug where first frame of cloud anim is shown in wrong pos
                    self.anim_state.reset()
                    self.transition(PLAYER_STATE.IDLE)
            
            case PLAYER_STATE.SHOOTING:
                
                self.trigger_shoot = False
                
                if self.anim_state.done:
                    self.anim_state.reset()
                    self.transition(PLAYER_STATE.IDLE)
        
        if self.border_check(frame_time):
            self.pos.x += self.velocity.x * frame_time
        
        self.anim_state.update(frame_time)
        
        if self.anim_state.row != PLAYER_STATE.DODGING: #workaround for having different texture for dodging with row being 0
            self.player_frame = self.anim_state.frame(self.anim_state.row)
        else:
            self.player_frame = self.anim_state.frame(0)
        self.player_frame.width *= self.direction
        
        self.destination_rectangle.x = self.pos.x
        self.collision_rectangle.x = self.pos.x + SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE * HITBOX_WIDTH_RATIO
    
    def manage_cooldowns(self, frame_time):
        if self.shooting_cooldown_left > 0:
            self.shooting_cooldown_left -= frame_time
        if self.dashing_cooldown_left > 0:
            self.dashing_cooldown_left -= frame_time
    
    def shoot(self):
        self.transition(PLAYER_STATE.SHOOTING)
        self.shooting_cooldown_left = self.shooting_cooldown
        self.trigger_shoot = True
    
    def dodge(self):
        self.velocity.x = self.direction * PLAYER_DODGE_SPEED    
        self.dashing_cooldown_left = self.dashing_cooldown
    
    def move_left(self):
        self.direction = Direction.LEFT
        self.velocity.x = self.direction * PLAYER_SPEED
        self.transition(PLAYER_STATE.WALKING)
    
    def move_right(self,):
        self.direction = Direction.RIGHT
        self.velocity.x = self.direction * PLAYER_SPEED
        self.transition(PLAYER_STATE.WALKING)
    
    def border_check(self, frame_time):
        
        will_be_inside_right = self.pos.x + self.velocity.x * frame_time + (SPRITE_SHEET_TILE_SIZE * PLAYER_SCALE) - 40 < WINDOW_WIDTH
        will_be_inside_left = self.pos.x + self.velocity.x * frame_time + 40 > 0
        return will_be_inside_left and will_be_inside_right
        
    def draw(self, is_hitbox_mode):
        
        if self.anim_state.row == PLAYER_STATE.DODGING:
            self.player_texture = self.dodge_texture
        else:
            self.player_texture = self.normal_texture
        
        #draw player duh
        draw_texture_pro(
            self.player_texture,
            self.player_frame,
            self.destination_rectangle,
            Vector2(0,0),
            0.0,
            WHITE
        )
        
        #show lines around player in hitbox mode
        if is_hitbox_mode:
            draw_rectangle_lines(int(self.collision_rectangle.x), int(self.collision_rectangle.y), int(self.collision_rectangle.width), int(self.collision_rectangle.height), GREEN)
        
        if self.dodge_cloud.active:
            self.dodge_cloud.draw()
        
        
        
        #dash meter indicator
        if self.dashing_cooldown_left <= 0:
            dash_box_color = GREEN
        elif self.dashing_cooldown_left <=.5:
            dash_box_color = YELLOW
        else:
            dash_box_color = RED
        
        draw_rectangle_rounded_lines_ex(Rectangle(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 150, 20, 110),1.0, 10, 2, PURPLE)
        starting_height_dash_box = (WINDOW_HEIGHT - 20) - int(130 * (1 - self.dashing_cooldown_left / self.dashing_cooldown))
        draw_rectangle_rounded(Rectangle(WINDOW_WIDTH - 100, starting_height_dash_box, 20, (WINDOW_HEIGHT - 40) - starting_height_dash_box), 1.0, 10, dash_box_color)
        
        draw_texture_ex(self.dash_icon_texture, Vector2(WINDOW_WIDTH - 100, WINDOW_HEIGHT- 35), 0.0, .5, WHITE)
        
        #shoot meter indicator
        if self.shooting_cooldown_left <= 0:
            shoot_box_color = GREEN
        
        elif self.shooting_cooldown_left <=.5:
            shoot_box_color = YELLOW
        
        else:
            shoot_box_color = RED
       
        draw_rectangle_rounded_lines_ex(Rectangle(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 150, 20, 110),1.0, 10, 2, ORANGE)
        starting_height_shoot_box = (WINDOW_HEIGHT - 20) - int(130 * (1 - self.shooting_cooldown_left / self.shooting_cooldown))
        draw_rectangle_rounded(Rectangle(WINDOW_WIDTH - 50, starting_height_shoot_box, 20, (WINDOW_HEIGHT - 40) - starting_height_shoot_box), 1.0, 10, shoot_box_color)
        draw_texture_ex(self.attack_icon_texture, Vector2(WINDOW_WIDTH - 55, WINDOW_HEIGHT- 35), 0.0, .5, WHITE)
        draw_circle_gradient(WINDOW_WIDTH - 40, WINDOW_HEIGHT - 170, 15, WHITE, RED)
        
        if self.shooting_vertical:
            draw_texture_ex(self.up_arrow_texture, Vector2(WINDOW_WIDTH - 56, WINDOW_HEIGHT - 185), 0.0, .5, WHITE)
        else:
            draw_texture_ex(self.right_arrow_texture, Vector2(WINDOW_WIDTH - 56, WINDOW_HEIGHT- 185), 0.0, .5, WHITE)
            
class Background:
    
    def __init__(self):
        self.frame = 0
        self.timer = 0

        self.frameRec = Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.BG_dest = Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        
    def startup(self):
        self.texture = load_texture(join('assets', 'background.png'))
        self.bridge_texture = load_texture(join('assets', 'bridge.png'))
        self.bridge_frameRec = Rectangle(0, 0, self.bridge_texture.width, self.bridge_texture.height)
        self.bridge_dest = Rectangle(BRIDGE_OFFSETX, BRIDGE_OFFSETY, BRIDGE_LENGTH, BRIDGE_HEIGHT)
    
    def update(self, frame_time):
        #DECIDED TO KEEP OLD ANIMATION LOGIC BECAUSE BACKGROUND ANIMATION IS NOT 64 by 64 TILED SPRITE SHEET
        self.timer += frame_time

        if self.timer >= BG_DUR:
            self.timer = 0
            self.frame += 1

            if self.frame >= BG_FRAME_COUNT:
                self.frame = 0

        self.frameRec.x = self.frame * WINDOW_WIDTH 

    def draw(self):
        draw_texture_pro(
            self.texture,
            self.frameRec,
            self.BG_dest,
            (0,0),
            0,
            WHITE
        )
        draw_texture_pro(
            self.bridge_texture,
            self.bridge_frameRec,
            self.bridge_dest,
            (0,0),
            0,
            WHITE
        )        
class Shoot:
    
    def __init__(self):
        self.position = Vector2(0,0)
        self.velocity = Vector2(0,0)
        self.active = False
        self.vertical = True
        self.horizontal_direction = Direction.RIGHT
        self.collision_rectangle = Rectangle(self.position.x, self.position.y, SHOOT_WIDTH, SHOOT_HEIGHT)
        
        self.anim_state = Animation(
            first=0, last=6, cur=0,
            step = 1, duration = SHOOT_DURATION, duration_left = SHOOT_DURATION,
            anim_type=AnimationType.ONESHOT, 
            row=1, sprites_in_row=7
        )
        
        self.shoot_frame = self.anim_state.frame(self.anim_state.row)
    
    def reset(self):
        self.position = Vector2(-100, -100)
        self.velocity = Vector2(0,-SHOOT_SPEED)
        self.active = False
        self.vertical = True
        self.horizontal_direction = Direction.RIGHT
        self.collision_rectangle = Rectangle(self.position.x, self.position.y, SHOOT_WIDTH, SHOOT_HEIGHT)
        
        self.anim_state = Animation(
            first=0, last=6, cur=0,
            step = 1, duration = SHOOT_DURATION, duration_left = SHOOT_DURATION,
            anim_type=AnimationType.ONESHOT, 
            row=1, sprites_in_row=7
        )
        self.shoot_frame = self.anim_state.frame(self.anim_state.row)
    
    def startup(self):
        self.texture = load_texture(join('assets', 'curse_cloud.png'))
        pass
    
    def update(self,frame_time):
        
        if self.vertical:
            self.velocity = Vector2(0, -SHOOT_SPEED * frame_time)
        else:
            self.velocity = Vector2(SHOOT_SPEED * self.horizontal_direction * frame_time, 0)
        
        self.anim_state.update(frame_time)
        self.shoot_frame = self.anim_state.frame(self.anim_state.row)
        
        self.position = vector2_add(self.position, self.velocity)
        self.collision_rectangle.x = self.position.x
        self.collision_rectangle.y = self.position.y
        
        if self.anim_state.done:
            self.active = False
            self.anim_state.reset_oneshot()
    
    def draw(self, is_hitbox_mode):
        
        if self.active:
            destination_rec = Rectangle(self.position.x, self.position.y, 64, 64)
            draw_texture_pro(self.texture, self.shoot_frame, destination_rec, (0,0), 0, WHITE)
            
            if is_hitbox_mode:  
                draw_rectangle_lines(int(self.position.x), int(self.position.y), SHOOT_WIDTH, SHOOT_HEIGHT, GREEN)

class Dodge_Cloud:
    def __init__(self):
        
        self.active = False
        self.position = Vector2(-100,-100)
        self.anim_state = Animation(
            first=0, last=4, cur=0,
            step = 1, duration = DODGE_CLOUD_DUR, duration_left = DODGE_CLOUD_DUR,
            anim_type=AnimationType.ONESHOT, 
            row=0, sprites_in_row=5
        )
        self.frame = self.anim_state.frame(self.anim_state.row)
        self.destination_rectangle = Rectangle(self.position.x, self.position.y, 64, 64)
    
    def reset(self):
        
        self.active = False
        self.position = Vector2(-100,-100)
        self.anim_state = Animation(
            first=0, last=4, cur=0,
            step = 1, duration = DODGE_CLOUD_DUR, duration_left = DODGE_CLOUD_DUR,
            anim_type=AnimationType.ONESHOT, 
            row=0, sprites_in_row=5
        )
        self.frame = self.anim_state.frame(self.anim_state.row)
        self.destination_rectangle = Rectangle(self.position.x, self.position.y, 64, 64)
    
    def startup(self):
        self.texture = load_texture(join('assets', 'dodge_cloud.png'))
    
    def update(self, frame_time):
        
        if self.anim_state.done:
            self.active = False
            self.anim_state.reset_oneshot()
            return
        
        self.destination_rectangle.x = self.position.x
        self.destination_rectangle.y = self.position.y
        self.anim_state.update(frame_time)
        self.frame = self.anim_state.frame(self.anim_state.row)
    
    def draw(self):
        draw_texture_pro(self.texture, self.frame, self.destination_rectangle, (0,0), 0, WHITE)
        
class Ball:
    
    def __init__(self, direction, idx, texture):
        
        self.texture = texture
        self.position = Vector2(0,0)
        self.velocity = Vector2(0,0)
        self.radius = 0.0
        self.points = 0
        self.idx = idx
        self.children_idxs = [self.idx * 2 + 2, self.idx * 2 + 3] #algorithm can be put in readme for why this is
        self.active = False
        
        self.frame = 0
        self.anim_state = Animation(
            first = 0, last = 4, cur = 0,
            step = 1, duration = EYEBALL_BLINK_DUR, duration_left = EYEBALL_BLINK_DUR,
            anim_type = AnimationType.REPEATING,
            row = 0, sprites_in_row = 5
        )
        self.facing_direction = direction
        self.frame = self.anim_state.frame(self.anim_state.row)
        self.destination_rectangle = Rectangle(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, self.radius * 2)  
         
    def update(self,frame_time):
        
        delta_position = Vector2(self.velocity.x * frame_time, self.velocity.y * frame_time)    
        self.position = vector2_add(self.position, delta_position)
            
        #bouncing off of side walls
        if self.position.x + self.radius > WINDOW_WIDTH or self.position.x - self.radius < 0:
            self.velocity.x *= -1
            if self.position.x + self.radius > WINDOW_WIDTH:
                self.position.x = WINDOW_WIDTH - self.radius
            elif self.position.x - self.radius < 0:
                self.position.x = self.radius
        
        #bouncing off of the ground
        if self.position.y + self.radius > GROUND_LEVEL:
            self.velocity.y *= COEFFICIENT_OF_RESTITUTION
            self.position.y = GROUND_LEVEL - self.radius
        self.velocity.y += GRAVITY * frame_time
        
        self.destination_rectangle.x = self.position.x - self.radius * (1.3) #offset manually tested
        self.destination_rectangle.y = self.position.y - self.radius * (1.3)
        self.destination_rectangle.width = self.radius * 2 * (1.3) 
        self.destination_rectangle.height = self.radius * 2 * (1.3)
        
        self.anim_state.update(frame_time)
        self.frame = self.anim_state.frame(self.anim_state.row)
        self.frame.width *= self.facing_direction
    
    def draw(self, hitbox_mode):
        
        if hitbox_mode:
            draw_circle_lines_v(self.position, self.radius, GREEN)
        draw_texture_pro(self.texture, self.frame, self.destination_rectangle, (0,0), 0, WHITE)

class Display_point:
    
    def __init__(self, position, value):
        self.position = position
        self.value = value
        self.duration_left = DISPLAY_POINTS_DUR
        self.is_active = True
    
    def update(self, frame_time):
        self.duration_left -= frame_time
        if self.duration_left <= 0:
            self.is_active = False
    
    def draw(self):
        draw_text(f"+{self.value}", int(self.position.x), int(self.position.y), 20, YELLOW)

