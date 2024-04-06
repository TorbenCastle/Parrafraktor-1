import configparser
from controller import Controller
from stepper import Stepper
import threading


class Data_handler:
    def __init__(self):
        self.config_lock = threading.Lock()
        


################################ CREATE CLASS OBJECTS ######################################
    def create_parrafraktor_from_cfg(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path)

        section_name = 'parrafraktor_1'
        if section_name not in config:
            raise ValueError(f"Section '{section_name}' not found in the config file.")

        parrafraktor_cfg = config[section_name]
        return Controller(
            name=section_name,
            dmx_address=int(parrafraktor_cfg['dmx_address']),
            min_speed=float(parrafraktor_cfg['min_speed']),
            acceleration=float(parrafraktor_cfg['acceleration']),
            steps=int(parrafraktor_cfg['steps']),
            run_mode=str(parrafraktor_cfg['run_mode']),
            dmx_mode=int(parrafraktor_cfg['dmx_mode']),
            universe=int(parrafraktor_cfg['universe']),
            subnet=int(parrafraktor_cfg['subnet']),
            net=int(parrafraktor_cfg['net']),
            data_handler = self
        
        )

    def create_steppers_from_cfg(self, file_path, controller):
        config = configparser.ConfigParser()
        config.read(file_path)
        dmx_address = controller.dmx_address
        dmx_mode = controller.dmx_mode
        stepper_list = []
        for section_name in config.sections():
            if section_name.startswith('stepper_'):
                stepper_cfg = config[section_name]
                stepper = Stepper(
                    name=section_name,
                    pulse_pin=int(stepper_cfg['step_pin']),
                    direction_pin=int(stepper_cfg['dir_pin']),
                    en_pin=int(stepper_cfg['en_pin']),
                    dir_invert=str(stepper_cfg['dir_invert']),
                    full_revolution_mode=str(stepper_cfg['full_revolution_mode']),
                    position=int(stepper_cfg['position']),
                    controller=controller,
                    start_dmx_address=dmx_address,
                    dmx_mode=dmx_mode,
                    run_mode=controller.run_mode,
                    data_handler = self
                    # Pass the ConfigHandler instance to Stepper
                )
                #add the dmx channels to steppers
                dmx_address += dmx_mode
                stepper_list.append(stepper)
                print(section_name)
        return stepper_list


    def read_section_key_value(self, file_path, section_name , key):
            
          config = configparser.ConfigParser()  
          self.config_lock.acquire()  
          config.read(file_path)
          value = config.get(section_name, key)
          self.config_lock.release()
          return value
 ######################################## WRITE TO CONFIG  ###############################################  
    
    def write_to_config(self, file_path, section_name, key, value):
        config = configparser.ConfigParser()
        with open(file_path, 'r+') as configfile:
            self.config_lock.acquire()

            config.read_file(configfile)

            if section_name not in self.config:
                print(f"{section_name} not found")

            config.set(section_name, key, str(value))

            # Go to the beginning of the file and truncate it to clear its content
            configfile.seek(0)
            configfile.truncate()

            # Write the updated configuration to the file
            config.write(configfile)

            self.config_lock.release()
