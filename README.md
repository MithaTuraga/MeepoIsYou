# MeepoIsYou

Introduction 
----------------------------------------------------------
This project is a python replication of the game Baba Is You, where the user is given the ability to change the rules of the game as they play. Please free to check out a demo of the orginal game https://www.youtube.com/watch?v=U4W_9rfjSus. 


Tools
----------------------------------------------------------
* Pycharm 
* Python 
* OOP concepts and Game Logic 



FEATURES 
-----------------------------------------------------------------
This project is a little different, the rules change as you go!! The player always starts off as Meepo due to the rule Meepo Is You, however as Meepo moves around the blocks, the rules change and objects begin to adapt. It is a constantly updating game platform! 


FILES
------------------------------------------------------------------

- sprites; this folder holds the images of all the players and objects on the screen, sprites are used throughout the program and you can see them at use when running the logic. 
- maps; this folder holds the text files of the different maps that we use for the game layout, you can see that there currently exist 11 different maps 
- actor.py; This module contains the Actor class and all its subclasses that represent different types of elements in the game.
- game.py; This module contains the Game class and the main game application.
- settings.py; This module contains the settings and global variables needed for the game configurations. 
- stack.py; This module contains the constant reading and updating of the information on the game board. It stores data in a last-in, first-out order. When removing an item from the stack, the most recently-added item is the one that is removed.
- student_tests.py; This module contains various test cases, to check and build on the functionality of the program. 

GETTING STARTED
---------------------------------------------------------------

**Project Link:** https://github.com/MithaTuraga/MeepoIsYou.git

**Important:** The main function in game.py runs the game and starts the GUI. Maps are located in the maps directory
and maps are saved as .txt files with the pieces on the game board. 

