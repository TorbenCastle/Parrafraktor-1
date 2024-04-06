class LCD_menu():
    def __init__(self, name):
        self.name = name
        # Define the menu structure
        self.menu_structure = {
            "Menu 1: Status": ["IP ADDRESS", "ON Time"],
            "Menu 2: Input": ["DMX", "MANUAL"],
            "Menu 3: Set channels": {
                "Stepper 1": ["ch 1", "ch 2", "ch 3", "ch 4"],
                "Stepper 2": ["ch 1", "ch 2", "ch 3", "ch 4"],
                "Stepper 3": ["ch 1", "ch 2", "ch 3", "ch 4"]
            }
        }
        self.current_menu = "Menu 1: Status"
        self.display_menu(self.menu_structure[self.current_menu])

    # Function to display menus
    def display_menu(self, menu):
        print(self.current_menu)
        for item in menu:
            print("- " + item)

    # Function to handle moving up in the menu
    def handle_up_button(self):
        # Logic to handle moving up in the menu
        menus = list(self.menu_structure.keys())
        current_index = menus.index(self.current_menu)
        if current_index > 0:
            self.current_menu = menus[current_index - 1]
            self.display_menu(self.menu_structure[self.current_menu])

    # Function to handle moving down in the menu
    def handle_down_button(self):
        # Logic to handle moving down in the menu
        menus = list(self.menu_structure.keys())
        current_index = menus.index(self.current_menu)
        if current_index < len(menus) - 1:
            self.current_menu = menus[current_index + 1]
            self.display_menu(self.menu_structure[self.current_menu])

    # Function to handle selection or entering a submenu
    def handle_enter_button(self):
        # Logic to handle selection or entering a submenu
        selection = input("Enter submenu selection: ")
        if selection in self.menu_structure[self.current_menu]:
            print("Selected:", selection)
        elif selection in self.menu_structure[self.current_menu]:
            self.current_menu = selection
            self.display_menu(self.menu_structure[self.current_menu])
        else:
            print("Invalid selection")

    # Function to handle exiting the current menu or going back to the previous menu
    def handle_exit_button(self):
        # Logic to handle exiting the current menu or going back to the previous menu
        print("Exiting", self.current_menu)
        self.current_menu = "Menu 1: Status"
        self.display_menu(self.menu_structure[self.current_menu])

    # Loop to continuously display the current menu and handle user input
    def run_menu(self):
        while True:
            user_input = input("Enter button press: ")

            if user_input == "up":
                self.handle_up_button()
            elif user_input == "down":
                self.handle_down_button()
            elif user_input == "enter":
                self.handle_enter_button()
            elif user_input == "exit":
                self.handle_exit_button()
            else:
                print("Invalid input")

# Create an instance of the menu and run it
menu_instance = LCD_menu("Main Menu")
menu_instance.run_menu()
