
import threading
from threading import Thread
import time
import socket
from stupidArtnet import StupidArtnetServer
from serial_dmx import SerialDMX
import stepper as Stepper

 #this class is the main controlling part of the program  
class Controller():
    def __init__(self, name, dmx_address, min_speed , acceleration, steps , run_mode , dmx_mode , universe , subnet , net , data_handler ):
        self.name                 = name
        self.dmx_address          = dmx_address    
        self.min_speed            = min_speed
        self.acceleration         = acceleration
        self.steps                = steps
        self.run_mode             = run_mode
        self.dmx_mode             = dmx_mode
    
        self.universe             = universe
        self.subnet               = subnet
        self.net                  = net
    

        self.ip                   = self.get_ip_address()
        self.artnet               = StupidArtnetServer()
        self.serial_dmx           = SerialDMX('/dev/ttyUSB0', 250000, 1)
    
        self.u1_listener = self.artnet.register_listener(
        self.universe, callback_function=None)
    
        #time to startup arnet
        time.sleep(1)
        self.data_handler = data_handler
        self.steppers = None
        self.LCD = None
    
    def get_ip_address(self):
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
            # Connect to a remote server
            s.connect(("8.8.8.8", 80))
        
            # Get the local IP address
            ip_address = s.getsockname()[0]
        
            return ip_address
        except Exception as e:
            print("Error getting IP address:", e)
            return None
        
############################################# GETTERS ####################################################


    def get_name(self):
        return self.name
    
    def get_dmx_address(self):
        return self.dmx_address
    
    def get_min_speed(self):
        return self.min_speed
    def get_acceleration(self):
        return self.acceleration
    
    def get_steps(self):
        return self.steps
    
    def get_run_mode(self):
        return self.run_mode
    
    def get_dmx_mode(self):
        return self.dmx_mode
    
    def get_universe(self):
        return self.universe
    
    def get_subnet(self):
        return self.subnet
    
    def get_net(self):
        return self.net       

############################################# SETTERS ####################################################

    # Setters
    def set_name(self, name):
        self.name = name
    
    def set_dmx_address(self, dmx_address):
        self.dmx_address = dmx_address
    
    def set_min_speed(self, min_speed):
        self.min_speed = min_speed
    
    def set_steps(self, steps):
        self.steps = steps
    
    def set_run_mode(self, run_mode):
        self.run_mode = run_mode
    
    def set_dmx_mode(self, dmx_mode):
        self.dmx_mode = dmx_mode
    
    def set_universe(self, universe):
        self.universe = universe
    
    def set_subnet(self, subnet):
        self.subnet = subnet
    
    def set_net(self, net):
        self.net = net
        
