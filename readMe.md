SECTIONS:
ELEVATOR PITCH AND DETAILED OVERVIEW
KEY FEATURES
SCREENSHOTS
LIST OF RESOURCES USED
TRAILER



!!!ELEVATOR PITCH AND DETAILED OVERVIEW!!!

Pang Of The Damned: Classic pang with a Hellscape theme and differentiating shoot and dodge mechanics. 

Detailed overview:
    Structure: game_enums.py for enums used elsewhere
    anim.py: hosts animation file that makes square animations easy
    objects.py: every individual instance object like class player, ball, shoot, display point, etc
    pang.py: main engine of game, handles interactions between classes in objects.py and hosts the balls class 
    settings.py: used to prevent "magic numbers" configures settings of the game
    
    *2 enemy eyeballs which must be shot at to split and split into medium size and then small size for a total of 13 balls needed to be shot
    
    *Because of coefficient of restitution balls continuosly get lower as they bounce
    
    *Dodge mechanic: in a tricky spot where you are about to get hit, press space to dodge/dash quickly in an invulnerable state to a safe spot
    
    *changing shoot direction: unlike normal pang, in pang of the damned, player is able to toggle between a horizontal and vertical shot by pressing right click
    
    *players can dodge and shoot while idling or walking, but must wait to return to idle after dodging or shooting and for cooldowns to replenish to shot or dodge again

    *cooldown mechanics: player needs to be critical with their timing of shots and dashes since these actions have cooldowns
    
    *score counter and individual enemy score rendering

    *Animations: (player shooting, dodging, idling, walking, dying), enemy eyeball blinking, background animation, and projectile animation where cloud dissipates, dash cloud animation that renders at a players location when they press dash

    *music and sound effects: background theme music, player shooting sfx, player dashing sfx, player dying sfx, enemy split or die sfx, 

    *easy game reset function so you can get back into the action

    screens: splash, playing, instructions, pause, GAME_OVER(lost), win screen

    DEBUG and dev tools: hitbox mode, make player invincible, game speed decrementer and incrementer


!!!KEY FEATURES!!!:


BALL CHILDREN INDEXING: ![alt text](game_screenshots/ball_indexing.png)

PLAYER COOLDOWNS (SHOOTING and DASHING):
similar to anim.py, there are stored variables for duration and duration left, called shooting/dashing cooldown for duration and shooting/dashing_cooldown_left for how much time is left.

cooldown left indicates how much time you have to wait until player can perform a shoot or dodge, every player update, if the cooldown_left > 0, we decrement it:
 
 def manage_cooldowns(self, frame_time):
        if self.shooting_cooldown_left > 0:
            self.shooting_cooldown_left -= frame_time
        if self.dashing_cooldown_left > 0:
            self.dashing_cooldown_left -= frame_time
    
 If player state is in IDLE or Walking, player may perform one of these actions if also the cooldown left <= 0. The cooldown left is also used to calculate the starting y position of the cooldown bars for the cooldown indicator in the bottom right:

 starting_height_dash_box = (WINDOW_HEIGHT - 20) - int(130 * (1 - self.dashing_cooldown_left / self.dashing_cooldown))
        draw_rectangle_rounded(Rectangle(WINDOW_WIDTH - 100, starting_height_dash_box, 20, (WINDOW_HEIGHT - 40) - starting_height_dash_box), 1.0, 10, dash_box_color)

starting height of the cooldown indicator is calculated by subtracting from the bottom of the indicator (ie the empty y value), the top offset multiplied by the percent of cooldown left / cooldown total duration. if percent is  100% then bar is green, if between 99 and 50, yellow, and below that red.

Dodging MECHANIC: 
Collision detection between ball and player only sets the player state to dying and game over IF the player is not in the dodging_anim state. Simple anim state check for this feature

TRIGGER_SHOOT MECHANIC:
Problem: simply putting the player state into shooting doesn't make it such that a shoot is rendered, ie how do we get the main game loop to know to activate a shoot just because the player is in the shooting. (PLAYER doesn't store a shoot object). Solution: store a trigger_shoot flag in player that can be accessed in the pang.py update file because Game stores the player and when the player transitions to shoot set this flag as true which allows the game to active the projectile: 

def check_shoot_activation(self):
        if self.player.trigger_shoot:
            if not self.shoot.active:
                self.shoot.position = Vector2(self.player.collision_rectangle.x +  self.player.collision_rectangle.width / 2, self.player.pos.y)
                self.shoot.active = True
                self.shoot.vertical = self.player.shooting_vertical
                self.shoot.horizontal_direction = self.player.direction

CHANGING_SHOOT_DIRECTION MECHANIC:
    pretty simple mechanic, but store a shootin_vertical flag in the player state. In the player update function, listen for a right mouse click which will negate this flag in any player state. When a shoot is triggered, the velocity of the shoot is determined by this flag. 
    if player.shooting_vertical: 
        velocity of shoot = (0,-shoot_speed)
    else:
        velocity of shoot = (shoot_speed * player_direction, 0)

HITBOX_MODE_MECHANIC:
    objects store is hitbox mode flag, and when toggled draw functions will draw rect_lines around the hitbox

GAME_SPEED_MECHANIC:
    all update functions are dependent on one call to get frame_time in the main game update function and this is multiplied by game speed which can be incremented or decremented by the player pressing up arrow or down arrow. 

Invincible player mode:
    collision check also checks self.invulnerable mode and only transitions to player dying if this is false


!!!SCREENSHOTS!!!:

Progression: 
![alt text](game_screenshots/splash.png)
![alt text](game_screenshots/instructions.png)
![alt text](game_screenshots/win_screen.png)
![alt text](game_screenshots/dead.png)
![alt text](game_screenshots/defeat.png)
![alt text](game_screenshots/playing.png)

Key Features screenshots:

![alt text](game_screenshots/hitbox_mode.png)
![alt text](game_screenshots/invulnerability_dodge.png)
![alt text](game_screenshots/horizontal_shoot.png)
![alt text](game_screenshots/vertical_shoot.png)
![alt text](game_screenshots/dash_cooldown.png)
![alt text](game_screenshots/shoot_cooldown_demo.png)


!!!LIST OF RESOURCES USED!!!:

TUTORIALS, TOOLS, PEOPLE: 

*Problem with accessing enum values (dependency issue): had trouble determing how to access player anim state values from both pang.py and objects, so I asked chatgpt what it thought I should do and it said to avoid circular dependencies I should put it in a separate file, so from now on I have an enum.py file to store enums which will be useful when I ed up implementing the enum values for game state as well. NOTE: chat did not code i just asked for its advice in this situation

*How to load and use sound and music in pyray: 

https://www.raylib.com/examples/audio/loader.html?name=audio_music_stream

https://www.raylib.com/examples/audio/loader.html?name=audio_sound_loading

*Starter code for anim.py and transition and state for player: utilized in class activity code from animation_camera.py (Partner was Vincent)

*C code reference: https://github.com/raysan5/raylib-games/blob/master/classics/src/pang.c used for deciding what objects to make and what fields should be

*Balls class implementation: Asked professor Fourquet with respect on how to refactor my balls handling and she said to utilize one balls class with necessary methods such that game class wasn't so cluttered

SPRITES: 

attack_icon.png: GENERATED BY GOOGLE GEMINI

background.png: https://share.google/MWfBkYp1Gql7JVUwQ

bridge.png : https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fcraftpix.net%2Ffreebies%2Ffree-bridges-top-down-pixel-art-asset-pack%2F%3Fsrsltid%3DAfmBOoqxuckB9PPMjaY284MKpQmvTJLBuVy-rEKE_OqBDXugAWOEB0Mi&ved=0CBoQjhxqFwoTCMij7abqmpMDFQAAAAAdAAAAABAH&opi=89978449

curse_cloud.png : google gemini

dash_icon png : google gemini

defeat screen : chatgpt ai image generation

dodge_cloud : google gemini

eyeball.png : google gemini

instruction_backsplash.png: google gemini

left_click_icon.png : https://share.google/9HlGUEI5WQY6Ee7Tz

pause_screen.png: chatgpt ai image generation

right_click_icon.png : https://share.google/knE91Kmrma0gp5dch

sideways.png : https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fthenounproject.com%2Fbrowse%2Ficons%2Fterm%2Fhorizontal-arrows%2F&ved=0CBYQjRxqFwoTCLjMrMyG2pMDFQAAAAAdAAAAABAH&opi=89978449

skeleton_dodge.png : sourced from skeleton_player.png

skeleton_player.png : https://astrobob.itch.io/animated-pixel-art-skeleton

splash_screen.png : chat gpt ai image generation and google gemini (originally gemini but then reformed using chatgpt)

up.png : https://www.google.com/imgres?q=up%20arrow&imgurl=https%3A%2F%2Fwww.clipartmax.com%2Fpng%2Fmiddle%2F445-4454869_ios-arrow-thin-up-svg-png-icon-free-download-thin-up-arrow.png&imgrefurl=https%3A%2F%2Fwww.clipartmax.com%2Fmiddle%2Fm2H7d3G6H7m2H7N4_ios-arrow-thin-up-svg-png-icon-free-download-thin-up-arrow%2F&docid=9l87wmiMA5ynjM&tbnid=ez0WFsl39Q1QUM&vet=12ahUKEwih-LGJiNqTAxXlrokEHVSFAh8QnPAOegQIXxAB..i&w=840&h=1060&hcb=2&ved=2ahUKEwih-LGJiNqTAxXlrokEHVSFAh8QnPAOegQIXxAB

victory_screen.png : chat gpt image generation

MUSIC AND SOUND EFFECTS:

background_music.mp3 : https://pixabay.com/music/hard-rock-heavy-doom-dark-metal-493397/

death_sound_effect.mp3 : https://pixabay.com/sound-effects/people-man-death-scream-186763/

dodge_sound_effect.mp3 : https://pixabay.com/sound-effects/film-special-effects-whoosh-motion-405445/

eyeball_pop_sound_effect.mp3 : https://pixabay.com/sound-effects/film-special-effects-bone-breaking-393842/

shooting_sound_effect.mp3 : https://pixabay.com/sound-effects/film-special-effects-magical-whoosh-148459/


!!!TRAILER!!!
https://youtu.be/ed4Jp-5SU5M

https://drive.google.com/file/d/1kx_XXtugi7iliryaCvGUtXdxSQPd6uoE/view?usp=sharing