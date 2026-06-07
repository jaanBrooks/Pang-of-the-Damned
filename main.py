from raylib import *
from pang import *
from settings import * 

if __name__ == '__main__':  

  init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Python Game")
  init_audio_device()
  set_target_fps(TARGET_FPS)

  current_game = Game()

  current_game.startup()

  while not window_should_close():

    current_game.update()
      
    begin_drawing()
    clear_background(BLUE)

    current_game.draw()

    end_drawing()
close_audio_device()
close_window()
  