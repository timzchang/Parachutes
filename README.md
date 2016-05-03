# Parachutes - cse30332 Final project. 

##Intro
  A 2-player networked game of Parachutes. The roles are split between:
  1. Dropper: drops Cyborg Parachute troops on the base
  2. Defender: protects the base by shooting 10x10 blocks at the falling cyborgs

##How to play
Both players log into student02.cse.nd.edu and run the python script corresponding to their preferred roles. (Dropper runs dropper.py, Defender runs defender.py). Once both players run their scripts, the game should connect automatically and the game will begin.

More generally, this program can be run on any computer with an open port. To do this, edit the dropper.py file and the defender.py file so that "port" is set to an open TCP port. After this edit, both scripts should be run on the same machine with the following commands from the `src/` directory:

1: Player 1 (defender)
```bash
python defender.py
```
2: Player 2 (dropper)
```bash
python dropper.py
```

The scripts can be started in any order. Once the two scripts are run, they will automatically connect and start the game.

##Defender
###Objective:
Defender wins when it exhausts all of Dropper's troops without losing all its lives. Defender begins with unlimited ammunition and 5 lives. It loses one life for every parachuter that makes its way to the bottom of the screen. The defender loses when it runs out lives. 

###Gameplay:
The shooting mechanic of the Defender follows a simple point and click method. The barrel tracks the movement of the mouse, and fires as quickly as the user can click. Some cyborgs may need to be hit more than one time before it gets destroyed!

###Controls:
Mouse position - aim the gun

Mouse click - fire a bullet

##Dropper
###Objective:
Dropper wins when it depletes Defender's lives. Dropper begins with 5 different kinds of troops, numbering 75 in total. If Dropper exhausts all its troops without depleting Defender's lives, Dropper loses.

###Gameplay
Dropper is equipped with 5 different Cyborg classes:

![alt tag](https://raw.githubusercontent.com/timzchang/Parachutes/master/media/parachute.png)

1: Normal (Brown)
  * Health: 2
  * Speed: Normal
  * Skill: None
  * Stock: 20

![alt tag](https://raw.githubusercontent.com/timzchang/Parachutes/master/media/purple_parachute.png)

2: Teleporter (Purple)
  * Health: 2
  * Speed: Normal
  * Skill: On hit, teleports to a random location on screen
  * Stock: 15

![alt tag](https://raw.githubusercontent.com/timzchang/Parachutes/master/media/blue_parachute.png)

3: Speedster (Blue)
  * Health: 2
  * Speed: Fast
  * Skill: None
  * Stock: 15

![alt tag](https://raw.githubusercontent.com/timzchang/Parachutes/master/media/red_parachute.png)

4: Swayer (Red)
  * Health: 2
  * Speed: Normal
  * Skill: Sways back and forth
  * Stock: 15

![alt tag](https://raw.githubusercontent.com/timzchang/Parachutes/master/media/green_parachute.png)

5: Tank (Green)
  * Health: 7
  * Speed: Slow
  * Skill: None
  * Stock: 10

Each cyborg is mapped to the 1-5 number keys. Dropper selects its troop and clicks on the screen to select the x-position from which to drop it. A counter on the screen shows the remaining stock of each cyborg.

###Controls
1 keyboard button - select Normal cyborg to drop

2 keyboard button - select Teleporter cyborg to drop

3 keyboard button - select Speedster cyborg to drop

4 keyboard button - select Swayer cyborg to drop

5 keyboard button - select Tank cyborg to drop

Mouse click - drop the selected cyborg (if you have any of that kind left)
