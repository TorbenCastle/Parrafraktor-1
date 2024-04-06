try:
    import RPi.GPIO as GPIO
    on_raspberry_pi = True
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

except ImportError:
    on_raspberry_pi = False
import time
import threading



class Stepper():
    
    def __init__(self, name, pulse_pin , direction_pin,  en_pin , dir_invert , full_revolution_mode ,
                 position  ,controller , start_dmx_address , 
                 dmx_mode, run_mode , data_handler):
               
        self.name = name

        #stepper PIN config
        self.PULSE_pin = pulse_pin  # Stepper Drive Pulses
        self.DIR_pin = direction_pin  # Controller Direction Bit (High for Controller default / LOW to Force a Direction Change).
        self.EN_pin = en_pin  # Controller EN_pin Bit (High to EN_pin / LOW to Disable).
        
        #little workarround to convert str to booelans
        self.DIR_invert = self.str_to_bool(dir_invert)  #invert direction
        self.full_revolution_mode = self.str_to_bool(full_revolution_mode)

        #stepper variables
        self.position = position
        self.target = 0
        self.last_target = 0
        

        self.min_speed = controller.get_min_speed()
        self.acceleration = controller.get_acceleration()
        self.steps = controller.get_steps()
        
        self.speed = 0 
        self.last_direction = 0
        self.last_speed = 0
        
        #dmx channel handle       
        self.channel_mode = dmx_mode
        self.start_dmx_address = start_dmx_address
        
        self.channel_values = [0] * self.channel_mode
            
        #other stepper handle values
        self.go_cw = 1
        self.go_cww = -1                
        self.is_running = False
        self.stop = False
        self.initialaized = True    
       
        
        self.speed_param_1 = 0.08
        self.speed_param_2 = 15
        

        #main control object init
        self.controller = controller
        self.dmx_mode = dmx_mode
        
        #stepper running mode
        self.run_mode = run_mode     
        self.stepper_lock = threading.Lock()
        self.data_handler = data_handler
        self.man_value_changed = False

        #GPIO part for raspberry


        if on_raspberry_pi == True:
            GPIO.setup(self.DIR_pin, GPIO.OUT)
            GPIO.setup(self.PULSE_pin, GPIO.OUT)           

            if (self.DIR_invert):
                self.DIR_left = GPIO.LOW
                self.DIR_right = GPIO.HIGH
            else:        
                self.DIR_left = GPIO.HIGH
                self.DIR_right = GPIO.LOW    
                
        if (self.DIR_invert == False):
            print(f"INVERT: {self.DIR_invert}")
        

#################################################### GETTER #######################################################

    def get_name(self):
        return self._name

    def get_pulse_pin(self):
        return self._pulse_pin

    def get_dir_pin(self):
        return self._dir_pin

    def get_EN_pin(self):
        return self._EN_pin

    def get_position(self):
        return self._position

    def get_speed(self):
        return self._speed

    def get_min_speed(self):
        return self._min_speed

    def get_steps(self):
        return self._steps

    def get_last_direction(self):
        return self._last_direction

    def get_last_speed(self):
        return self._last_speed

    def get_start_dmx_address(self):
        return self._start_dmx_address

    def get_run_mode(self):
        return self._run_mode

    def get_is_running(self):
        return self._is_running

    def get_stop(self):
        return self._stop

    def get_initialized(self):
        return self._initialized



#################################################### SETTER #######################################################
    def set_name(self, name):
        self._name = name

    def set_position(self, position):
        self._position = position

    def set_speed(self, speed):
        self._speed = speed

    def set_min_speed(self, min_speed):
        self._min_speed = min_speed

    def set_steps(self, steps):
        self._steps = steps

    def set_start_dmx_address(self, start_dmx_address):
        self._start_dmx_address = start_dmx_address

    def set_mode(self, run_mode):
        self._run_mode = run_mode

    def set_is_running(self, is_running):
        self._is_running = is_running

    def set_stop(self, stop):
        self._stop = stop

    def set_initialized(self, initialized):
        self._initialized = initialized
        



#################################   MAIN STEPPER FUNCTIONS ################################################
   
    #write DIR pin to desired direction and set PULSE_pin to high and low with the delay of the stepper speed
    def make_step(self, target_direction, velocity):
        self.last_direction = target_direction
        self.last_speed = velocity
        #test if not on raspberry
        if on_raspberry_pi == False:
            self.make_virtual_step(target_direction, velocity)
            return
    #dont move is velocity is 0
        if velocity != 0:
            #set dir pin                          
            if(target_direction == self.go_cw):               
                GPIO.output(self.DIR_pin, self.DIR_right)                
            elif(target_direction == self.go_cww):
                GPIO.output(self.DIR_pin, self.DIR_left)   
            self.is_running = True 
            #Puls modulieren
            GPIO.output(self.PULSE_pin, GPIO.HIGH)
            time.sleep(velocity)

            GPIO.output(self.PULSE_pin, GPIO.LOW)
            time.sleep(velocity)          
            
            #add last move to position
            self.position += target_direction
            self.last_direction = target_direction
            self.last_speed = velocity
        else:
            self.last_speed = 0
            self.is_running = False
            time.sleep(0.1)#just a little timeout
       
          

    #virtual movement method
    def make_virtual_step(self, target_direction, velocity):
        #dont move is velocity is 0
        if velocity != 0:
            #set dir pin                 
            self.is_running = True 
            #Puls modulieren            
            time.sleep(velocity)           
            time.sleep(velocity)          
            
            #add last move to position
            self.position += target_direction
           
            self.last_direction = target_direction
            self.last_speed = velocity
        else:
            self.last_speed = 0
            self.is_running = False
            time.sleep(0.1)#just a little timeout
        #if the motor made a 180° turn, reset the pos to zero    
        #self.check180()          
    
    
    def move_to_position(self, target , speed):
        if self.position != target and not self.stop:  
            print(f"{self.name} to {target} with speed {speed}  at position {self.position} ")    

            self.make_step(self.go_cw if target > self.position else self.go_cww, speed)
        else:
            self.last_speed = 0

    #blocking move to target position method without acceleration
    def move_fast_to_position(self, target):
        while self.position != target and not self.stop:                      
            # Move with the new speed
            self.make_step(self.go_cw if self.target > self.position else self.go_cww, self.calculate_speed_channel(self.channel_values[2]))
    
     




    #calculate coarse position target
    def calculate_coarse_target(self, channel_value ):
        
        if (self.run_mode == "DMX" or self.run_mode == "ARTNET"):
            low = 0
            mid = 127
            high = 255
        elif self.run_mode == "MAN":
            low = -self.steps
            mid = 0
            high = self.steps    

        #depending on the full or half rotation count boolean, the dmx values are calculated to full or half positions.
        #half positions are more fine. we do this later ########################################################################
        dmx_steps = self.steps

        #calculate coarse target with dmx channel
        if channel_value == low:
            coarse_target = -dmx_steps            
        elif channel_value == mid:
            coarse_target = 0
        elif channel_value == high:
            coarse_target = dmx_steps
        #calculate dmx value to position   
        else:
            if channel_value < mid:
                coarse_target = self.scale_value(channel_value ,low , mid , -self.steps , 0 )   
            elif channel_value > mid:
                coarse_target = self.scale_value(channel_value ,mid , high , 0 , self.steps ) 
        #round first channel value
        coarse_target = int(round(coarse_target))    
        
        return coarse_target   
    
    #calculate fine position target 
    def calculate_fine_target(self, channel_value):
        
        if self.mode == "DMX":
            low = 0
            mid = 127
            high = 255
        elif self.mode == "MAN":
            low = -self.steps
            mid = 0
            high = self.steps    
        #calculate coarse target with dmx channel 
        if channel_value == mid:
            fine_target = 0    
        else:
            if channel_value < mid:
                fine_target = self.scale_value(channel_value ,low , mid , -self.steps , 0 )   
            elif channel_value > mid:
                fine_target = self.scale_value(channel_value ,mid , high , 0 , self.steps ) 
        #round first channel value
        fine_target = int(round(fine_target))
        
        return fine_target
    
    # check for continious rotation or set target depending on dmx value and if on extended dmx mode, it can use an other source than "DMX" to calcluate debug or manual positions
    def calculate_target(self, channel_A , channel_B):     
        if channel_A == 0 and channel_B == 0:           
                target = -2 * self.steps
                return target
        elif channel_A == 255 and channel_B == 255:                      
                target = 2 * self.steps
                return target
        else: 
            #combine coarse and fine target
            target = self.calculate_coarse_target(channel_A) + self.calculate_coarse_target(channel_B)
        return target
        
    
    #parameters are only testet a bit!
    #input is a dmx or manual value between 0 and 255 output is     0.5% to 100%    
    def calculate_speed_channel(self, speed_value):
        if(speed_value == 0):
            return 0
        calculated_speed = self.speed_param_1 * (self.scale_value(speed_value , 0 , 255, 0.5, 100.0))
        if(calculated_speed == 0):
            return 0.1275       
        target_speed = (self.speed_param_2 * self.min_speed / calculated_speed)        
        return target_speed
    

    
     
    #run program on dmx mode (default)  
    def mode_dmx(self):
        
        #read out channel values
        self.read_dmx_channels()
        
        #calculate target from dmx channel 1 and 2
        self.target = self.calculate_target(self.channel_values[0] , self.channel_values[1])
        
        #calculate speed from channel 3
        self.speed = self.calculate_speed_channel(self.channel_values[2])
        
        #move to position.
        self.move_to_position(self.target , self.speed)
        #if velocity is 0 or position is reached
     #run program on dmx mode (default)  

    def mode_artnet(self):
        
        #read out channel values
        self.read_artnet_channels()
        
        #calculate target from dmx channel 1 and 2
        self.target = self.calculate_target(self.channel_values[0] , self.channel_values[1])
        
        #calculate speed from channel 3
        self.speed = self.calculate_speed_channel(self.channel_values[2])
        
        #move to position.
        self.move_to_position(self.target, self.speed)
        #if velocity is 0 or position is reached  

    def mode_manual(self):
        if self.man_value_changed == True:
            self.man_value_changed == False
            for i in self.channel_values:
                self.get_manual_channel_value(i)
                
        #calculate target from dmx channel 1 and 2
        self.target = self.calculate_target(self.channel_values[0] , self.channel_values[1])
        
        #calculate speed from channel 3
        self.speed = self.calculate_speed_channel(self.channel_values[2]) 
       
        
        if (self.position == self.target):
           self.last_speed = 0
        else:
            self.move_to_position(self.target , self.speed)        
       
        


 ################################################# CHANNEL INPUT DATA  ####################################################

    #get dmx values     
    def read_artnet_channels(self):        
        buffer = self.controller.artnet.get_buffer(self.controller.u1_listener)
        
        #we need to store the dmx value for channel 1 at index 0 from dmx buffer channel 1  . not 0!
        if buffer != None:
            for i, _ in enumerate(self.channel_values):  
                self.channel_values[i] = int(buffer[self.start_dmx_address + i - 1])
                           
        else:
            print("NO ARTNET INPUT")
            
    def read_dmx_channels(self):
        for i in self.channel_values:
            self.controller.serial_dmx.get_channel_value(i)
        
            
    #store manually setted values from controller object 
    def set_manual_channel_value(self, channel , value):
        with self.stepper_lock:
         self.channel_values[channel] = value
         self.man_value_changed = True
    
    #read manual setted values
    def get_manual_channel_value(self, channel):
        with self.stepper_lock:
            return self.channel_values[channel]


####################################################### OTHER STEPPER FUNCTIONS ########################################


    #scale values from dmx or other input     
    def scale_value(self , value, input_min  , input_max , output_min , output_max):
    # Scale the value to the new range
        scaled_value = ((value - input_min) / (input_max - input_min)) * (output_max - output_min) + output_min
        return int(scaled_value)               

    def check180(self):
        if(self.position == self.steps or self.position == -self.steps):
            self.setPosition(0)            
 
    def invert_driection(self):
        if self.DIR_invert == False:   
            self.DIR_left = GPIO.LOW
            self.DIR_right = GPIO.HIGH
            self.DIR_invert = True
            
        elif self.DIR_invert == True:
             self.DIR_left = GPIO.HIGH
             self.DIR_right = GPIO.LOW
             self.DIR_invert = False
             
        #write to config
        return self.DIR_invert   
    
    #the config parser does not read my bools correct..
    def str_to_bool(self, s):
        s = s.lower()  # Convert to lowercase for case-insensitive comparison
        if s in ['1', 'yes', 'true']:
            return True
        elif s in ['0', 'no', 'false']:
            return False
        else:
            raise ValueError("Invalid input. Input must be '1', 'yes', 'True', '0', 'no', or 'False'.")
        

    def print_stepper_info(self):
        print(f"NAME {self.name} STEP_PIN {self.PULSE_pin} DIR_PIN {self.DIR_pin} DIR_INVERT {self.DIR_invert} MODE {self.run_mode} POSITION {self.position}")


    def stepper_write_to_config(self, section, value):

        self.data_handler.write_to_config("config/stepper.cfg", self.name , section, value)




######################################################## MAIN STEPPER LOOP ####################################################
    #start sequence    
    def start(self):
        self.print_stepper_info()
    
        #by changeing setting self.initialaized to False we delete the stepper object.
        while(self.initialaized):
            if self.run_mode == "DMX":
                print(self.run_mode)
                while(self.run_mode == "DMX" and self.stop == False):
                    self.mode_dmx()
            elif self.run_mode == "ARTNET":
              print(self.run_mode)
              while(self.run_mode == "ARTNET" and self.stop == False):
                self.mode_artnet()        
            elif self.run_mode == "MAN":
                print(self.run_mode)
                while(self.run_mode == "MAN" and self.stop == False):
                    self.mode_manual()
                    #self.position += 1
                #self.stepper_write_to_config("position" , self.position)
                #self.data_handler.read_section_key_value("config/stepper.cfg", self.name ,"position")
                #time.sleep(0.8)
                #self.print_stepper_info()
                #print(f"Name: {self.name}")
                #self.read_artnet_channels()
                      
          
            
        
    


