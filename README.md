# Parachutes - cse30332 Final project. 

##Intro
  A 2-player networked game of Parachutes. The roles are split between
  1. Dropper: drops Cyborg Parachute troops on the base
  2. Defender: protects the base by shooting 10x10 blocks at the falling cyborgs

##How to play
Both players log into student02.cse.nd.edu and run the python script corresponding to their preferred roles. (Dropper runs dropper.py, Defender runs defender.py). Once both players run their scripts, the game should connect automatically and the game will begin.

##Defender
###Objective:
Defender wins when it exhausts all of Dropper's troops without losing all its lives. Defender begins with unlimited ammunition and 5 lives. It loses one life for every parachuter that makes its way to the bottom of the screen. 

###Gameplay:
The shooting mechanic of the Defender follows a simple point and click method. The barrel tracks the movement of the mouse, and fires as quickly as the user can click.

##Dropper
###Objective:
Dropper wins when it depletes Defender's lives. Dropper begins with 5 different kinds of troops, numbering 75 in total. If Dropper exhausts all its troops without depleting Defender's lives, Dropper loses.

###Gameplay
Dropper is equipped with 5 different Cyborg classes:

1. Normal (Brown)
  * Health: 2
  * Speed: Normal
  * Skill: None
  * Stock: 20
2. Teleporter (Purple)
  * Health: 2
  * Speed: Normal
  * Skill: On hit, teleports to a random location on screen
  * Stock: 15
3. Speedster (Blue)
  * Health: 2
  * Speed: Fast
  * Skill: None
  * Stock: 15
4. Swayer (Red)
  * Health: 2
  * Speed: Normal
  * Skill: sways back and forth
  * Stock: 15
5. Tank (Green)
  * Health: 7
  * Speed: Slow
  * Skill: None
  * Stock: 10

Each cyborg is mapped to the 1-5 number keys. Dropper selects its troop and clicks on the screen to select the x-position from which to drop it. A counter on the screen shows the remaining stock of each cyborg.
