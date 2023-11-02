#!/usr/local/bin/python3
# coding: utf-8
import curses
import sys
import numpy as np
import random
from time import sleep
from math import floor

delay = 1
scrx = 10
scry = 20

def main(stdscr):
    global yscale, xscale
    freezeMode = False
    debugMode = False
    matrixMode = False
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    stdscr.keypad(True)
    if delay == 0:
        stdscr.nodelay(True)
    else:
        curses.halfdelay(1)
    stdscr.clear()
    if curses.LINES >= 42:
        yscale = 2
        xscale = 3
    else:
        yscale = 1
        xscale = 1
    offScreenY = 6
    sideBar = 6
    hiddenRows = offScreenY * yscale
    startY = hiddenRows - yscale * 2
    rows = min((scry + 1) * yscale + hiddenRows,
               (curses.LINES + hiddenRows) // yscale * yscale)
    cols = min((scrx + 2) * xscale, (curses.COLS - 2 * sideBar) // xscale * xscale)
    origy = curses.LINES // 2 - (rows - hiddenRows) // 2
    origx = curses.COLS // 2 - cols // 2 - sideBar
    parkedTetros = np.zeros((rows, cols + 2 * sideBar), dtype=int)
    gameScreen = np.zeros((rows, cols + 2 * sideBar), dtype=int)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK) # for debug mode
    curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK) # for debug mode
    red, green, blue = curses.color_content(curses.COLOR_WHITE)
    curses.init_color(curses.COLOR_WHITE, red, green // 2, 0) 
    curses.init_color(curses.COLOR_MAGENTA, red // 2, 0, blue // 2) 
    tetrominoes = [ np.array([[ 1, 1, 1, 1 ]], dtype=int),
                   
                    np.array([[ 2, 0, 0 ],
                              [ 2, 2, 2 ]], dtype=int),
                   
                    np.array([[ 0, 0, 3 ],
                              [ 3, 3, 3 ]], dtype=int),
                   
                    np.array([[ 4, 4 ],
                              [ 4, 4 ]], dtype=int),

                    np.array([[ 0, 5, 5 ],
                              [ 5, 5, 0 ]], dtype=int),

                    np.array([[ 0, 6, 0 ],
                              [ 6, 6, 6 ]], dtype=int),
                    
                    np.array([[ 7, 7, 0 ],
                              [ 0, 7, 7 ]], dtype=int) ]

    centres = [ np.array( [[ 2 ], [ -0.5 ]], dtype=int),
                np.array( [[ 1 ], [ -0.5 ]], dtype=int),
                np.array( [[ 1 ], [ -0.5 ]], dtype=int),
                np.array( [[ 1 ], [ -1   ]], dtype=int),
                np.array( [[ 1 ], [ -0.5 ]], dtype=int),
                np.array( [[ 1 ], [ -0.5 ]], dtype=int),
                np.array( [[ 1 ], [ -0.5 ]], dtype=int) ]

    rotor = np.array([[  0, 1 ],
                      [ -1, 0 ]], dtype=int)

    scale = ( yscale, xscale )

    ones = np.ones( scale, dtype=int )
    
    tetros = [ tetrominoes ]
    for i in range(1,4):
        tetros.append([ np.rot90(t)for t in tetros[ i-1 ] ])   

    for i in range(0,4):
        tetros[i] = [ np.kron(t, ones) for t in tetros[i] ]

    offsets = [ centres ]
    for i in range(1,4):
        offsets.append( [ rotor.dot(o) for o in offsets[ i-1 ] ] )

    tetroX = -1
    tetroY = -1
    selection = -1
    tetro = None
    holdSelection = -1
    holdOK = True
    rotation = 0
    offset = None
    score = 0
    hiscore = 0
    sevenBag = [ i for i in range(0,7) ]
    sevenBagIndex = None
    piecePipe = None
    TheMatrix = [ 'ç', 'ｸ', '7', 'ﾊ', 'ﾐ', 'ﾋ', 'ｰ', 
                  'ｳ', 'ｼ', 'ﾅ', 'ﾓ', 'ﾆ', 'ｻ', 'ﾜ', 
                  'ﾂ', 'ｵ', 'ﾘ', 'ｱ', 'ﾎ', 'ﾃ', 'ﾏ', 
                  'ｹ', 'ﾒ', 'ｴ', 'ｶ', 'ｷ', 'ﾑ', 'ﾕ', 
                  'ﾗ', 'ｾ', 'ﾈ', 'ｽ', 'ﾀ', 'ﾇ', 'ﾍ',
                  'Ɛ', 'Ɫ','ᔭ', 'ᴚ', '⊥', '∀' ]

    def newGame():
        nonlocal parkedTetros, score, freezeMode
        nonlocal score, piecePipe, sevenBagIndex, tetro, holdSelection
        nonlocal holdOK, freezeMode, debugMode, matrixMode
        parkedTetros[ 0:rows + hiddenRows, 0:cols + 2 * sideBar ] = 0
        parkedTetros[ rows - yscale:rows, sideBar:cols + sideBar ] = 3
        parkedTetros[ 0:rows, sideBar:sideBar + xscale ] = 3
        parkedTetros[ 0:rows, cols + sideBar - xscale:cols + sideBar ] = 3
        score = 0
        random.shuffle(sevenBag)
        piecePipe = []
        for i in range(0,6):
            piecePipe.append(sevenBag[i])
        sevenBagIndex = 6
        tetro = None
        holdSelection = -1
        holdOK = True
        freezeMode = False
        debugMode = False
        matrixMode = False
        
    def newTetro(held = -1):
        nonlocal selection, tetro, rotation, offset, tetroX, tetroY
        nonlocal sevenBagIndex, piecePipe
        rotation = 0
        if held == -1:
            selection = piecePipe.pop(0)
        else:
            selection = held
        piecePipe.append( sevenBag[ sevenBagIndex ] )
        sevenBagIndex += 1
        if sevenBagIndex == 7:
            random.shuffle(sevenBag)
            sevenBagIndex = 0
        tetro = tetros[ rotation ][ selection ]
        offset = offsets[ rotation ][ selection ]
        tetroY = startY 
        tetroX = (sideBar + cols // 2 - tetro.shape[1] % 2) // xscale * xscale

    def getBounds(tetro, offset):
        y1 = tetroY - abs(floor(offset[1,0])) * yscale 
        y2 = tetroY - abs(floor(offset[1,0])) * yscale + tetro.shape[0]
        x1 = tetroX - abs(floor(offset[0,0])) * xscale
        x2 = tetroX - abs(floor(offset[0,0])) * xscale + tetro.shape[1]
        return(y1, y2, x1, x2)
         
    def rotateTetro(r):
        nonlocal tetro, rotation, offset, tetroX, tetroY
        new_rotation = (rotation + r) % 4
        rotated = tetros[ new_rotation ][ selection ]
        c = offsets[ new_rotation ][ selection ]
        y1, y2, x1, x2 = getBounds(rotated, c)
        colZone = parkedTetros[ y1:y2, x1:x2 ]
        if colZone.shape != rotated.shape:
            return False
        if np.array_equal(np.abs(colZone) + np.abs(rotated),
                          np.maximum(np.abs(colZone), np.abs(rotated))):
            tetro = rotated
            offset = c
            rotation = new_rotation
            return True
        else:
            return False

    def buildScreen():
        nonlocal gameScreen
        gameScreen = parkedTetros * 1
        if tetro is not None:
            y1, y2, x1, x2 = getBounds(tetro, offset)
            ghost_y1 = y1
            ghost_y2 = y2
            while True:
                colZone = parkedTetros[ ghost_y1:ghost_y2, x1:x2 ]
                if np.array_equal(np.abs(colZone) + np.abs(tetro),
                                  np.maximum(np.abs(colZone), np.abs(tetro))):
                    ghost_y1 += 1
                    ghost_y2 += 1
                else:
                    ghost_y1 -= 1
                    ghost_y2 -= 1
                    break
            if y2 < ghost_y1:
                gameScreen[ ghost_y1:ghost_y2, x1:x2 ] += tetro * -1
            elif y2 < ghost_y2:
                gameScreen[ y2:ghost_y2, x1:x2 ] += tetro[ y2 - ghost_y1:, : ] * -1
            gameScreen[ y1:y2, x1:x2 ] += tetro
        y1 = hiddenRows
        for i in range(0,6):
            nextPiece = tetrominoes[ piecePipe[ 5 - i ] ]
            y, x = nextPiece.shape
            x1 = cols + sideBar + sideBar // 2 - x // 2
            gameScreen[ y1:y1+y, x1:x1+x ] += nextPiece
            y1 += y + 1
        if holdSelection != -1:
            holdPiece = tetrominoes[ holdSelection ]
            y, x = holdPiece.shape
            x1 = sideBar // 2 - x // 2
            y1 = hiddenRows
            gameScreen[ y1:y1+y, x1:x1+x ] += holdPiece

    def drawScreen():
        for y in range(hiddenRows, rows):
            for x in range(0, cols + sideBar * 2):
                dy = origy + y - hiddenRows + 2
                dx = origx + x
                if debugMode:
                    try:
                        if gameScreen[y,x] >= 0:
                            stdscr.addch( dy, dx, chr(gameScreen[y,x] + ord('0')),
                                          curses.color_pair(9))
                        else:
                            stdscr.addch( dy, dx, chr(-gameScreen[y,x] + ord('0')),
                                          curses.color_pair(10))
                    except:
                        pass
                elif matrixMode:
                    try:
                        if gameScreen[y,x] == 0:
                            stdscr.addch(dy, dx, ' ', curses.color_pair(9))
                        else:
                            stdscr.addch(dy, dx, TheMatrix[ y * x  % len(TheMatrix) ], 
                                         curses.color_pair(9)) 
                    except:
                        pass
                else:
                    try:
                        if gameScreen[y,x] >= 0:
                            stdscr.addch(dy, dx, ' ',
                                         curses.color_pair(( gameScreen[y,x] -1) % 8 + 1 )) 
                        else:
                            stdscr.addch(dy, dx, chr(0x2591),
                                         curses.A_REVERSE + curses.color_pair((-gameScreen[y,x]-1)%8+1)) 
                    except:
                        pass
                    
    def moveTetro(y,x):
        nonlocal tetroX
        nonlocal tetroY
        y1, y2, x1, x2 = getBounds(tetro, offset)
        y1 += y
        y2 += y
        x1 += x
        x2 += x
        colZone = parkedTetros[ y1:y2, x1:x2 ]
        if colZone.shape != tetro.shape:
            return False
        if np.array_equal(np.abs(colZone) + np.abs(tetro),
                          np.maximum(np.abs(colZone), np.abs(tetro))):
            tetroX += x
            tetroY += y
            return True
        else:
            return False

    def holdTetro():
        nonlocal holdSelection, holdOK
        held = holdSelection
        holdSelection = selection
        newTetro(held),
        holdOK = False
        
    def updateDisplay():
        buildScreen()
        drawScreen()
        stdscr.refresh()

    def parkTetro():
        nonlocal parkedTetros, tetro, holdOK
        y1, y2, x1, x2 = getBounds(tetro, offset)
        parkedTetros[ y1:y2, x1:x2 ] += tetro
        tetro = None
        holdOK = True

    def checkLines():
        nonlocal matrixMode
        scorePerRow = 1
        y = rows-yscale
        while y > hiddenRows:
            y1 = y - yscale
            y2 = y
            x1 = sideBar + xscale
            x2 = sideBar + cols - xscale
            if np.all(parkedTetros[ y1:y2, x1:x2 ]):
                for c in range(6,-1,-1):
                    gameScreen[ y1:y2, x1:x2 ] = c
                    drawScreen()
                    stdscr.refresh()
                    sleep(0.05)
                parkedTetros[ yscale:y, x1:x2 ] = parkedTetros[ 0:y-yscale, x1:x2 ]
                addToScore(scorePerRow)
                scorePerRow += 1
                updateDisplay()
                sleep(0.5)
            else:
                y-=yscale

    def pause(confirm_key):
        while True:
            c = stdscr.getch()
            if c != curses.ERR:
                return c == confirm_key

    def pauseQuit():
        clearMessage()
        displayMessage("Press Q to quit!")
        quit = pause(ord('q'))
        clearMessage()
        return quit

    def pauseEscQuit():
        if pause(27):
            return pauseQuit()
        else:
            clearMessage()
            return False
    
    def displayMessage(text):
        stdscr.addstr(origy, origx + cols // 2 + sideBar - len(text) // 2, text)
        stdscr.refresh()

    def clearMessage():
        stdscr.addstr(origy, 0, ' ' * curses.COLS)
        stdscr.refresh()

    def addToScore(n):
        nonlocal score
        score += n
        stdscr.addstr(origy + 1, origx + sideBar + cols - len(str(score)) - 5, '     ' + str(score))
        stdscr.addstr(origy + 1, origx + sideBar, str(hiscore) + '     ')
        
    def nextTetro():
        parkTetro()
        checkLines()
        newTetro()
        
    def gameOver():
        nonlocal score, hiscore
        quit = False
        if score > hiscore:
            displayMessage("New Hiscore!")
            quit = pauseEscQuit()
            hiscore = score
        if not quit:
            displayMessage("Game Over!")
            quit = pauseEscQuit()
        return quit
           
    def inputAndWait():
        nonlocal freezeMode, matrixMode, debugMode
        ns = 1
        if delay > 0.1:
            ns = int(delay / yscale // 0.1)
        n = ns
        while n > 0:
            c = stdscr.getch()
            if c == curses.ERR:
                n-=1
                continue
            elif c == curses.KEY_LEFT:
                for i in range(0,xscale):
                    if moveTetro(0,-1):
                        updateDisplay()
                        sleep(0.05)
            elif c == curses.KEY_RIGHT:
                for i in range(0,xscale):
                    if moveTetro(0,1):
                        updateDisplay()
                        sleep(0.05)
            elif c == curses.KEY_DOWN:
                if moveTetro(1,0):
                    updateDisplay()
                    n = ns
                elif freezeMode:
                    nextTetro()
            elif c == ord('/') and freezeMode:
                if moveTetro(-1,0):
                    updateDisplay()
            elif c == ord('z') or c == curses.KEY_UP:
                if rotateTetro(1):
                    updateDisplay()
            elif c == ord('x'):
                if rotateTetro(-1):
                    updateDisplay()
            elif c == ord('c') and (holdOK or freezeMode):
                holdTetro()
            elif c == ord('d'):
                debugMode = not debugMode
                if debugMode: matrixMode = False
            elif c == ord('m'):
                matrixMode = not matrixMode
                if matrixMode: debugMode = False
            elif c == ord('f'):
                freezeMode = not freezeMode
            elif c == ord(' '):
                while moveTetro(1,0):
                    updateDisplay()
                    sleep(0.001)
                while c != curses.ERR:
                    c = stdscr.getch()
                nextTetro()                    
                return False
            elif c == 27:
                return pauseQuit()
            n-=1
        return False

    try:
        quit = False
        while not quit:
            newGame()
            addToScore(0)
            updateDisplay()
            displayMessage("Press any key to start!")
            if pause(27):
                quit = pauseQuit()
                continue
            clearMessage()
            newTetro()
            while True:
                updateDisplay()
                if inputAndWait():
                    break
                if not freezeMode and not moveTetro(1,0):
                    if tetroY == startY:
                        quit = gameOver()
                        break
                    else:
                        nextTetro()
    except KeyboardInterrupt:
        pass
    
def help():
    print('-h : print this help and exit')
    print('-t : time in seconds between game rounds')
    print('\nPlay in a console of at least 42 rows to use big pieces.\n')    
    print('In game controls:')
    print('Arrow keys for left, right, soft down and rotate counter clockwise')
    print('z & x - rotate couter clockwise and clockwise') 
    print('c - swap piece in play out with piece in the hold')
    print('<space> - hard down')
    print('f - freeze mode')
    print('/ - up when in freeze mnode')
    print('d - debug mode')
    print('m - matrix mode')
    exit()

argc = 1
while argc < len(sys.argv):
    argv = sys.argv[argc]
    argc += 1
    if argv == '-h': help()
    if argv == '-t':
        if argc < len(sys.argv):
            try:
                delay = float(sys.argv[argc])
            except ValueError:
                delay = 1
            else:
                argc += 1

curses.wrapper(main)

