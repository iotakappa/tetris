Tetris in a console  
Michael Boyd - 02/11/2023

This curses version of Tetris will use 2x3 character blocks if your console is
at least 42 lines high, otherwise 1x1. It includes the hold, the six piece
preivew, the ghost piece, and lock delay.

The code uses numpy matrix operations for scaling and rotating pieces,
composing the game screen, collision detection and complete line detection.

Controls:
Left and Rights Arrows - move current piece left and right  
Down Arrow - "soft drop" - move current piece down faster  
Space Bar  - "hard drop" - move current piece straight down to the bottom  
Up Arrow   - Rotate current piece couterclockwise  
'z' & 'x'  - Rotate current piece counterclockwise and clockwise  
'c'        - Swap current piece with the piece in the hold  
'd'        - Debug Mode - display colour bitmap instead of coloured blocks  
'm'        - Matrix Mode - as in the movie  
'f'        - Freeze Mode - or ratherm, cheat mode  
'/'        - In Freeze Mode move current piece up  

Future development: 
Probably none, but maybe I'll add: 
 - levels with accelerating play 
 - better scoring 
 - score wiping on use of Freeze Mode 
 - add wall kicks

 
