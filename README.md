# pkmn-quiz  
Pokemon-Quiz  
Game idea: www.sporcle.com/games/g/pokemon  

# Introduction    
This quiz is inspired by `www.sporcle.com/games/g/pokemon` and expands on it.  
You can test your knowledge on Pokemon names from Generations 1-9 in German and English (and both).  

# Features  
You can combine any Generations from 1-9 as you wish. 
For each combination, it saves your highscore in form of the maximal number of correct answers or, if all answers were found, the minimal time needed to successfully complete the game.  
The "in-order-mode" allows you to practice your expert-knowledge by requiring an input in the order as they appear in the national dex (as provided by www.pokewiki.de).  
For the language "All", this mode changes slightly, since here you have to type the name in German and English in order to continue with the next item (the order of languages does not matter).  
Each completion of the game will provide you with a symbol displayed at the end of the highscore. Try to obtain all 5 symbols for each combination of generations.  

# Start-up  
To start the game, download the corresponding executable `pkmn-quiz.exe`. You need to have Python 3 installed in order to run it.  
You can also download the source files or clone the repository and execute the file `game.py` with python.  
To create the executable yourself, you can use the command `pyinstaller --onefile .\game.py` from the root-folder of the repository.  

# System requirements  
The code was tested on the following two systems, but most likely also other combinations are possible:  
- CentOS 7 with python 3.6.8  
- Windows 11 with python 3.12.0  
The following python packages are needed (most of which are very likely already installed):  
- tkinter  
- ctypes  
- glob  
- math  
- time  
- os  
- importlib  
