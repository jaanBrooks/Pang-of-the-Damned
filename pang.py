from pyray import *
from raylib import *
from random import randint, uniform
from os.path import join
from settings import *
from objects import *
from game_enums import *
class Game:

    def __init__(self):
        self.state = GAME_STATE.SPLASH
        self.player = Player()
        self.shoot = Shoot() #player projectile 
        self.background = Background()
        self.is_hitbox_mode = False
        self.points_to_display = set() #little points that pop up when you hit an eyeball
        self.balls = Balls()
        self.speed_multiplier = GAME_SPEED
    
    def startup(self):
        
        self.splash_screen = load_texture(join('assets', 'splash_screen.png'))
        self.instructions_screen = load_texture(join('assets', 'instruction_backsplash.png'))
        self.pause_screen = load_texture(join('assets', 'pause_screen.png'))
        self.win_screen = load_texture(join('assets', 'victory_screen.png'))
        self.lose_screen = load_texture(join('assets', 'defeat_screen.png'))
        self.left_click_icon = load_texture(join('assets', 'left_click_icon.png'))
        self.right_click_icon = load_texture(join('assets', 'right_click_icon.png')) 
        
        self.background_music = load_music_stream(join("sound_effects","background_music.mp3"))
        play_music_stream(self.background_music)
        self.music_volume = MUSIC_VOLUME
        set_music_volume(self.background_music, self.music_volume)
        
        self.player.startup()
        self.background.startup()
        self.balls.startup()
        self.shoot.startup()  
    
    def reset_game(self):
        
        self.speed_multiplier = GAME_SPEED
        self.state = GAME_STATE.PLAYING 
        
        self.is_hitbox_mode = False
        self.points_to_display.clear()
        
        self.player.reset()
        self.balls.reset()
        self.shoot.reset()
    
    def update(self):
        
        update_music_stream(self.background_music) #tutorial online said to call every update loop
        
        frame_time = get_frame_time()#this frame time is passed to every update function
        
        match self.state:
            
            case GAME_STATE.SPLASH:
                
                if is_key_pressed(KeyboardKey.KEY_ENTER):
                    self.state = GAME_STATE.PLAYING
                
                elif is_key_pressed(KeyboardKey.KEY_I):
                    self.state = GAME_STATE.INSTRUCTIONS_FROM_SPLASH_SCREEN #necessary differentiation between instructions from splash and from pause so we know where to navigate back to
            
            case GAME_STATE.INSTRUCTIONS_FROM_SPLASH_SCREEN:
                if is_key_pressed(KeyboardKey.KEY_B):
                    self.state = GAME_STATE.SPLASH
            
            case GAME_STATE.PAUSED:
                
                if is_key_pressed(KeyboardKey.KEY_P):
                    self.state = GAME_STATE.PLAYING
                
                elif is_key_pressed(KeyboardKey.KEY_Q):
                    self.reset_game()
                    self.state = GAME_STATE.SPLASH
                
                elif is_key_pressed(KeyboardKey.KEY_I):
                    self.state = GAME_STATE.INSTRUCTIONS_FROM_PAUSE_SCREEN  
            
            case GAME_STATE.INSTRUCTIONS_FROM_PAUSE_SCREEN:
                if is_key_pressed(KeyboardKey.KEY_B):
                    self.state = GAME_STATE.PAUSED
            
            case GAME_STATE.GAME_OVER | GAME_STATE.WIN:
                if is_key_pressed(KeyboardKey.KEY_R):
                    self.reset_game()          
                    
            case GAME_STATE.PLAYING:
                
                if is_key_pressed(KeyboardKey.KEY_UP) and self.speed_multiplier < 3.0:
                    self.speed_multiplier += 0.2
                    
                if is_key_pressed(KeyboardKey.KEY_DOWN) and self.speed_multiplier > 0.2:
                    self.speed_multiplier -= 0.1
                
                frame_time *= self.speed_multiplier
                
                if is_key_pressed(KeyboardKey.KEY_P):
                    self.state = GAME_STATE.PAUSED
                    return
                
                if is_key_pressed(KeyboardKey.KEY_H):
                    self.is_hitbox_mode = not self.is_hitbox_mode
                    self.balls.update_hitbox_mode(self.is_hitbox_mode)
                
                if is_key_pressed(KeyboardKey.KEY_I):
                    self.balls.invulnerable_mode = not self.balls.invulnerable_mode
                
                self.background.update(frame_time)
                self.player.update(frame_time)
                self.balls.update(frame_time)
                self.balls.check_and_handle_collision_player_and_ball(self.player)
                
                #check right after checking collision between player and ball logically
                if self.player.anim_state.row == PLAYER_STATE.DYING and self.player.anim_state.done:
                    self.state = GAME_STATE.GAME_OVER
                    return
                
                
                self.check_shoot_activation()
                
                #only update shoots and check collision if active 
                if self.shoot.active:
                    self.shoot.update(frame_time)
                    self.balls.check_and_handle_collision_shoot_and_ball(self.shoot, self.player, self.points_to_display)
                
                #points may have changed due to shoot
                self.update_points_to_display(frame_time)
                
                #player may have won after shooting ball
                if self.player.score >= WINSCORE:
                    self.state = GAME_STATE.WIN
    
    #helper for update (didn't seem necessary to make a whole shoot class like for balls since there's one)
    def check_shoot_activation(self):
        if self.player.trigger_shoot:
            if not self.shoot.active:
                self.shoot.position = Vector2(self.player.collision_rectangle.x +  self.player.collision_rectangle.width / 2, self.player.pos.y)
                self.shoot.active = True
                self.shoot.vertical = self.player.shooting_vertical
                self.shoot.horizontal_direction = self.player.direction
    
    #same for display points
    def update_points_to_display(self,frame_time):
        for point in self.points_to_display:
            if point.is_active:
                point.update(frame_time)                  
    
    def draw(self):
        
        match self.state:
            
            case GAME_STATE.SPLASH:
                
                draw_texture_pro(self.splash_screen, Rectangle(0,0,self.splash_screen.width, self.splash_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
                
                draw_text("START: [ENTER]", 300, 280, 20, WHITE)
                draw_text("INSTRUCTIONS: [I]", 300, 310, 20, WHITE)
                draw_text("QUIT: [ESC]", 300, 340, 20, WHITE)
                
                draw_text("DEVELOPED BY JAAN BROOKS", 10, WINDOW_HEIGHT - 30, 20, WHITE)
            
            case GAME_STATE.INSTRUCTIONS_FROM_SPLASH_SCREEN | GAME_STATE.INSTRUCTIONS_FROM_PAUSE_SCREEN:
                draw_texture_pro(self.instructions_screen, Rectangle(0,0,self.instructions_screen.width, self.instructions_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
                draw_text("INSTRUCTIONS:", 230, 40, 40, WHITE)
                draw_text(" <-- : [B]", 5, 0, 20, WHITE)
                draw_text("MOVE LEFT : [A]", 15, 100, 20, WHITE)
                draw_text("MOVE RIGHT : [D]", 15, 130, 20, WHITE)
                draw_text("SHOOT : ", 15, 160, 20, WHITE)
                draw_texture_pro(self.left_click_icon, Rectangle(0,0,self.left_click_icon.width, self.left_click_icon.height), Rectangle(105, 160, 20, 20), (0,0), 0, WHITE)

                draw_text("CHANGE SHOOT DIRECTION : ", 15, 190, 20, WHITE)
                draw_texture_pro(self.right_click_icon, Rectangle(0,0,self.right_click_icon.width, self.right_click_icon.height), Rectangle(320, 190, 20, 20), (0,0), 0, WHITE)
                draw_text("INVULNERABILITY DASH : [SPACE]", 15, 220, 20, WHITE)
                draw_text("DEBUG AND DEV TOOLS:", 150, 300, 40, WHITE)
                draw_text("TOGGLE HITBOX MODE : [H]", 15, 360, 20, WHITE)
                draw_text("TOGGLE INVULNERABILITY : [I]", 15, 390, 20, WHITE)
                draw_text("INCREASE GAME SPEED : [UP ARROW]", 15, 420, 20, WHITE)
                draw_text("DECREASE GAME SPEED : [DOWN ARROW]", 15, 450, 20, WHITE)
            
            case GAME_STATE.PAUSED:
                draw_texture_pro(self.pause_screen, Rectangle(0,0,self.pause_screen.width, self.pause_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
                draw_text("RESUME: [P]", 15, 30, 10, WHITE)
                draw_text("QUIT TO SPLASH SCREEN: [Q]", 15, 60, 10, WHITE)
                draw_text("INSTRUCTIONS: [I]", 15, 90, 10, WHITE)

            case GAME_STATE.GAME_OVER:
                
                draw_texture_pro(self.lose_screen, Rectangle(0,0,self.lose_screen.width, self.lose_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
                draw_text("RESTART: [R], QUIT : [ESC] ", WINDOW_WIDTH // 2 - 145, WINDOW_HEIGHT - 30, 20, WHITE)
            
            case GAME_STATE.WIN:
                
                draw_texture_pro(self.win_screen, Rectangle(0,0,self.win_screen.width, self.win_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
                draw_text("CONGRATS, YOU WIN!", WINDOW_WIDTH // 2 - 170, WINDOW_HEIGHT -80 , 40, GREEN)
                draw_text("RESTART: [R], QUIT : [ESC] ", WINDOW_WIDTH // 2 - 145, WINDOW_HEIGHT - 30, 20, WHITE)
            
            case GAME_STATE.PLAYING:
                
                self.background.draw()
                self.balls.draw()
                self.player.draw(self.is_hitbox_mode)
                self.shoot.draw(self.is_hitbox_mode)
                
                draw_text(f"Score: {self.player.score}", 10, 20, 30, RED)
                draw_text(f"FPS: {get_fps()}", WINDOW_WIDTH - 140, 10, 20, WHITE)
                draw_text(f"Speed: {self.speed_multiplier:.1f}x", WINDOW_WIDTH - 140, 30, 20, WHITE)
                   
                if self.balls.invulnerable_mode:
                    draw_text("INVULNERABILITY ON", 10, WINDOW_HEIGHT - 40, 20, GREEN)
                if self.is_hitbox_mode:
                    draw_text("HITBOX MODE ON", 10, WINDOW_HEIGHT - 20, 20, GREEN)
                
                #drawing little points that pop up when you hit eyeball
                self.draw_points_to_display()
        
    #helper for draw
    def draw_points_to_display(self):
        for point in self.points_to_display:
            if point.is_active:
                point.draw()
    
class Balls():
    
    def __init__(self):
        
        self.balls = []
        self.is_hitbox_mode = False
        self.invulnerable_mode = False #need this in here as well since balls needs to know whether to end game with player collision
    
    def startup(self):
        
        self.texture = load_texture(join('assets', 'eyeball.png'))
        self.eyeball_death_sound = load_sound(join("sound_effects","eyeball_pop_sound_effect.mp3"))
        
        self.initialize_ball_list()
    
    def reset(self):
        
        self.is_hitbox_mode = False
        self.invulnerable_mode = False
        
        self.balls.clear()
        self.initialize_ball_list()
    
    def initialize_ball_list(self):
        
        #these dicts make it easier to set ball values in loop below
        big = {"radius": BIG_BALL_RADIUS, "points": BIG_BALL_POINTS, "is_active": True}
        medium ={"radius": MEDIUM_BALL_RADIUS, "points": MEDIUM_BALL_POINTS, "is_active": False}
        small = {"radius": SMALL_BALL_RADIUS, "points": SMALL_BALL_POINTS, "is_active": False}
            
        for i in range(MAX_BIG_BALLS + MAX_MEDIUM_BALLS + MAX_SMALL_BALLS):
            if i % 2 == 0:
                direction = Direction.LEFT
            else:                
                direction = Direction.RIGHT
            ball = Ball(direction, i, self.texture)
            
            ball.velocity = Vector2(BALL_HORIZONTAL_SPEED, BALL_VERTICAL_SPEED)
            
            if i < MAX_BIG_BALLS:
                size = big
                ball.position.x = randint(BIG_BALL_RADIUS, WINDOW_WIDTH - BIG_BALL_RADIUS)
                ball.position.y = randint(BIG_BALL_RADIUS, BOTTOM_OF_BALL_SPAWN_AREA - BIG_BALL_RADIUS)
            
            elif i < MAX_BIG_BALLS + MAX_MEDIUM_BALLS:
                size = medium
            
            else:
                size = small
                
            ball.radius = size["radius"]
            ball.points = size["points"]
            ball.active = size["is_active"]
            
            self.balls.append(ball)
            
    def check_and_handle_collision_shoot_and_ball(self, shoot, player, display_points):
        
        for ball in self.balls:
            
            if not shoot.active:
                break
            if not ball.active:
                continue
            
            if CheckCollisionCircleRec(ball.position, ball.radius, shoot.collision_rectangle):
                
                play_sound(self.eyeball_death_sound)
                
                shoot.active = False
                shoot.anim_state.reset_oneshot()
                ball.active = False
                
                player.score += ball.points
                display_points.add(Display_point(ball.position, ball.points))
                
                if ball.radius != SMALL_BALL_RADIUS: #only big and medium split
                    self.balls[ball.children_idxs[0]].active = True
                    self.balls[ball.children_idxs[1]].active = True
                    
                    self.balls[ball.children_idxs[0]].position = Vector2(ball.position.x, ball.position.y)
                    self.balls[ball.children_idxs[1]].position = Vector2(ball.position.x, ball.position.y)
                    
                    self.balls[ball.children_idxs[0]].velocity = Vector2(-ball.velocity.x, ball.velocity.y)
                    self.balls[ball.children_idxs[1]].velocity = Vector2(ball.velocity.x, ball.velocity.y)
    
    def check_and_handle_collision_player_and_ball(self, player):
        
        for ball in self.balls:
            if not self.invulnerable_mode and player.anim_state.row != PLAYER_STATE.DODGING and ball.active and CheckCollisionCircleRec(ball.position, ball.radius, player.collision_rectangle):
                player.transition(PLAYER_STATE.DYING)
                break        
    
    def update_hitbox_mode(self, is_hitbox_mode):
        self.is_hitbox_mode = is_hitbox_mode
    
    def update(self,frame_time):
        for ball in self.balls:
            if ball.active:
                ball.update(frame_time)
    
    def draw(self):
        for ball in self.balls:
            if ball.active:
                ball.draw(self.is_hitbox_mode)
    
    
    
    
    #Legacy
    """ def _init_ball_group(self, dest_list, count, radius, points, start_active):
        for _ in range(count):
            if _ % 2 == 0:
                direction = Direction.LEFT
            else:                
                direction = Direction.RIGHT
            ball = Ball(direction)
            ball.startup()
            ball.velocity = Vector2(BALL_HORIZONTAL_SPEED, BALL_VERTICAL_SPEED)
            ball.radius = radius
            ball.points = points
            ball.active = start_active

            if start_active:
                ball.position = Vector2(
                    randint(0, WINDOW_WIDTH - radius),
                    randint(radius, BOTTOM_OF_BALL_SPAWN_AREA - radius),
                )
            else:
                ball.position = Vector2(-100, -100)

            dest_list.append(ball) """
            
    """ def check_and_handle_collision_shoot_and_ball(self, ball_size,shoot): 
            for ball in ball_size:
                if not shoot.active:
                    break
                if ball.active and CheckCollisionCircleRec(ball.position, ball.radius, Rectangle(shoot.position.x, shoot.position.y, SHOOT_WIDTH, SHOOT_HEIGHT)):
                    shoot.active = False
                    shoot.anim_state.reset_oneshot()
                    ball.active = False
                    self.player.score += ball.points
                    self.points_to_display.add(Display_point(ball.position, ball.points))
                    list_to_append_to = None
                    split_ball_count = None
                    if ball.radius == BIG_BALL_RADIUS:
                        list_to_append_to = self.mediumBalls
                        split_ball_count = "mediumBallCount"
                    if ball.radius == MEDIUM_BALL_RADIUS:
                        list_to_append_to = self.smallBalls
                        split_ball_count = "smallBallCount"
                    if list_to_append_to is not None:
                        for i in range(2):
                            split_ball = list_to_append_to[getattr(self, split_ball_count)]
                            split_ball.position = Vector2(ball.position.x, ball.position.y)
                            split_ball.active = True
                            setattr(self, split_ball_count, getattr(self, split_ball_count) + 1)
                            if i == 0:
                                split_ball.velocity = Vector2(-ball.velocity.x, ball.velocity.y)
                            else:
                                split_ball.velocity = Vector2(ball.velocity.x, ball.velocity.y) """
    """ def check_and_handle_collision_player_and_ball(self, ball_size):
        for ball in ball_size:
            if self.player.anim_state.row != PLAYER_STATE.DODGING and ball.active and CheckCollisionCircleRec(ball.position, ball.radius, self.player.collision_rectangle):
                self.player.transition(PLAYER_STATE.DYING)
                break """
                
    """  if self.state == "splash":
            if is_key_pressed(KeyboardKey.KEY_ENTER):
                self.state = "playing"
            return

        if self.state in ("game_over", "WIN"):
            if is_key_pressed(KeyboardKey.KEY_R):
                self.reset_game()
            if is_key_pressed(KeyboardKey.KEY_Q):
                close_window()
            return
        if self.state == "playing":    
            if is_key_pressed(KeyboardKey.KEY_P): # change it to a toogle
                self.paused = not self.paused
                # change it to a toogle
            if is_key_pressed(KeyboardKey.KEY_H):
                self.is_hitbox_mode = not self.is_hitbox_mode
                self.balls.update_hitbox_mode(self.is_hitbox_mode)    
            
            #ACTUAL GAME UPDATE LOGIC
            if  not self.paused: 
                
                #Background update
                self.background.update()
                
                #Player update
                self.player.update()
                
                #Ball updates
                self.balls.update()
                #COLLISON PLAYER AND BALLS
                self.balls.check_and_handle_collision_player_and_ball(self.player)
                
                #GAME MAY END AFTER COLLISION CHECK
                if self.player.anim_state.row == PLAYER_STATE.DYING and self.player.anim_state.done:
                    self.state = "game_over"
                    return
                
                #REACT TO SHOOT
                if self.player.trigger_shoot:
                    for shoot in self.shoots:
                        if not shoot.active:
                            shoot.position = Vector2(self.player.collision_rectangle.x +  self.player.collision_rectangle.width / 2, self.player.pos.y)
                            shoot.active = True
                            shoot.vertical = self.player.shooting_vertical
                            shoot.horizontal_direction = self.player.direction
                            break
                
                #SHOOT UPDATE
                for shoot in self.shoots:
                    if shoot.active:
                            shoot.update()

                #SEE IF SHOOT HITSd ANY BALLS
                for shoot in self.shoots:
                    if shoot.active: 
                        self.balls.check_and_handle_collision_shoot_and_ball(shoot, self.player, self.points_to_display)
                            
            #PLAYER MAY HAVE WON AFTER SCORING POINTS
            if self.player.score >= WINSCORE:
                self.state = "WIN"

            self.update_points_to_display() """
    """ #re-iniitialize all game variables to their starting values
    def initialize_shoots(self):
         for i in range(PLAYER_MAX_SHOTS):
            newShoot = Shoot()
            newShoot.startup()
            newShoot.position = Vector2(-100, -100)
            newShoot.velocity = Vector2(0, -SHOOT_SPEED)
            newShoot.active = False
            self.shoots.append(newShoot)   """ 
    """ if self.state == "splash":
            draw_texture_pro(self.splash_screen, Rectangle(0,0,self.splash_screen.width, self.splash_screen.height), Rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT), (0,0), 0, WHITE)
        
        elif (not self.paused):
            self.background.draw()
            
            self.balls.draw()
            
            self.player.draw(self.is_hitbox_mode)
            
            if self.shoot.active:
                self.shoot.draw(self.is_hitbox_mode)
                    
            draw_text(f"Score: {self.player.score}", 20, 50, 20, WHITE)
            
            self.draw_points_to_display()
            
            if self.state == "game_over" or self.state == "WIN":
                draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, Color(0, 0, 0, 180))
                if self.state == "game_over":
                    draw_text("GAME OVER", WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 - 40, 20, RED)
                elif self.state == "WIN":
                    draw_text("CONGRATS, YOU WIN!", WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 - 40, 20, GREEN)
                draw_text("Press R to restart, Q to quit", WINDOW_WIDTH // 2 - 145, WINDOW_HEIGHT // 2 + 35, 20, WHITE)
            
        else:      
            draw_text("GAME PAUSED! Press p to resume", 200, 200, 40, WHITE) """            