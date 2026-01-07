import commandLineLogic  # omit the .py, this is my websocketConnection.py file. It integrates as a module and I kind of behaves like a class
                            # You can call its functions in the schema: myModule.myFunction()

banner = """\033[31m
  _    _            _                
 | |  | |          (_)               
 | |__| | ___  _ __ _ _______  _ __  
 |  __  |/ _ \\| '__| |_  / _ \\| '_ \\ 
 | |  | | (_) | |  | |/ / (_) | | | |
 |_|  |_|\\___/|_|  |_/___\\___/|_| |_|

\033[0m"""

if __name__ == "__main__": 
    print(banner)
    commandLineLogic.initCLI()
