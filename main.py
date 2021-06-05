from machine import I2C, Pin, PWM
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import utime
import _thread

# I2C constants
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

button = Pin(15, Pin.IN, Pin.PULL_DOWN)
buzzer = PWM(Pin(17))
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

player_character   = bytearray([0x0e,0x0c,0x0e,0x04,0x0e,0x15,0x04,0x0a])
obstacle_character = bytearray([0x0e,0x15,0x1f,0x15,0x15,0x1f,0x15,0x0e])

class DinoGame(object):
    def __init__(self):
        self.score = 0
        self.speed = 0.2
        self.obstacle_pos = 15
        
        self.is_jumping = False
        
    def draw(self):
        # !! SCREEN IS NOT CLEARED BEFORE MULTIPLE DRAW CALLS !!!
        
        # Clear last obstacles
        if self.obstacle_pos < 15 and self.obstacle_pos >= 0:
            lcd.move_to(0, 1)
            lcd.putchar(' ')
            lcd.move_to(self.obstacle_pos+1, 1)
            lcd.putchar(' ')
        
        # Draw score
        lcd.move_to(0, 0)
        lcd.putstr(str(self.score))
        
        # Draw player
        if self.is_jumping:
            lcd.move_to(3, 0)
            lcd.putchar(chr(0))
            lcd.move_to(3, 1)
            lcd.putchar(' ')
        else:
            lcd.move_to(3, 0)
            lcd.putchar(' ')
            lcd.move_to(3, 1)
            lcd.putchar(chr(0))
            
        # Draw obstacle
        if self.obstacle_pos < 15 and self.obstacle_pos >= 0:
            lcd.move_to(self.obstacle_pos, 1)
            lcd.putchar(chr(1))   
     
    def update(self):
        self.obstacle_pos -= 1
        
        if self.obstacle_pos < 0:
            self.obstacle_pos = 15
            self.speed -= 0.01
        
        if self.obstacle_pos == 2:
            self.score += 1
            
        if self.is_jumping:
            self.is_jumping = False
        
        if button.value() and not self.is_jumping:
            self.is_jumping = True
            _thread.start_new_thread(play_jump_sound, ())
            
        if not self.is_jumping and self.obstacle_pos == 3:
            self.game_over()
            
        utime.sleep(self.speed)
        
    def game_over(self):
        lcd.clear()
        lcd.move_to(3, 0)
        lcd.putstr("GAME OVER")
        
        buzzer.freq(300)
        buzzer.duty_u16(1000)
        utime.sleep(1)
        buzzer.duty_u16(0)
        utime.sleep(3)
        
        main()
    
def main(): 
    # Add custom glyphs
    lcd.custom_char(0, player_character)
    lcd.custom_char(1, obstacle_character)
    
    # Menu
    lcd.backlight_on()
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("DinoRPI by Gines ")
    lcd.move_to(1, 1)
    lcd.putstr("Press to start")
        
    while not button.value():
        utime.sleep(0.1)
        
    lcd.clear()
    play_jump_sound()
    game = DinoGame()
    
    while True:
        game.update()
        game.draw()


def play_jump_sound():
    # Play first note
    buzzer.freq(800)
    buzzer.duty_u16(1000)
    utime.sleep(0.05)
    
    # Play second note
    buzzer.freq(950)
    utime.sleep(0.05)
    
    # Play third note
    buzzer.freq(1500)
    utime.sleep(0.1)
    
    # Stop buzzing
    buzzer.duty_u16(0)
        
if __name__ == '__main__':
    main()
