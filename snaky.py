
from threading import Timer
import random, pygame, sys
from pygame.locals import *

FPS = 10
# WINDOWWIDTH = 640
# WINDOWHEIGHT = 480
WINDOWWIDTH = 1040
WINDOWHEIGHT = 840
CELLSIZE = 40
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

# Color setting
#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
GOLD      = (153, 153,   0)
GRAY      = (128, 128, 128)
BGCOLOR = BLACK


# Control setting
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    # New game setting, Initialize
    pygame.init()
    # Frame
    FPSCLOCK = pygame.time.Clock()
    # Game display setting, Size
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    # Font setting
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    # Show 'Snaky'
    pygame.display.set_caption('Snaky')

    # Show start screen
    showStartScreen()
    # Run game and Show GameOver screen
    while True:
        runGame()
        showGameOverScreen()

# Run game class
def runGame():
    list = [] # initialize black apple location list
    global score # initialize score
    score = 0
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    # First direction is RIGHT
    direction = RIGHT

    # Start apples in a random place.
    # Create apple
    apple = getRandomLocation(wormCoords,list)
    
    # Create black apple
    black = black_random(wormCoords,list,apple)
    # Add first black apple
    list.append(black)
    
    # Create gold apple
    gold = getRandomLocation(wormCoords,list)
    

    while True: # main game loop
        pre_direction = direction
        for event in pygame.event.get(): # event handling loop
                # Quit game command
            if event.type == QUIT:
                terminate()

                # Control key
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN

                    # Quit game command
                elif event.key == K_ESCAPE:
                    terminate()
        # Check if the worm has hit the edge or itself
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # Check if worm has eaten an apple (score +1, worm-len +1)
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # Don't remove worm's tail segment
            apple = getRandomLocation(wormCoords,list) # Set a new apple somewhere
            black = black_random(wormCoords,list,apple)
            list.append(black)
            score += 1

        else:
            del wormCoords[-1] # Remove worm's tail segment

        # Check if worm has eaten an gold apple (score +1, worm-len -1)
        if wormCoords[HEAD]['x'] == gold['x'] and wormCoords[HEAD]['y'] == gold['y'] or wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            if random.randrange(1,100) % 2 == 0:
                gold = gold_random(wormCoords,list, apple) # Set a new gold apple somewhere
                score += 1
                if len(wormCoords) < 2:
                    return # gameover
                del wormCoords[-1]

        # Check if worm has eaten an black apple
        for temp in list:
            if wormCoords[HEAD]['x'] == temp['x'] and wormCoords[HEAD]['y'] == temp['y']:
                return # gameover


        # Move the worm by adding a segment in the direction it is moving
        if not examine_direction(direction, pre_direction):
            direction = pre_direction
        # Move UP
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        # Move DOWN
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        # Move LEFT
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        # Move RIGHT
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        # Add new head
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        # Call drawGrid()
        drawGrid()
        # Call drawWorm(wormCoords)
        drawWorm(wormCoords)
        drawApple(apple)
        drawGold(gold)
        drawBlack(black)
        drawList(list)
        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# Can't move the One direction
def examine_direction(temp , direction):
    if direction == UP:
        if temp == DOWN:
            return False
    elif direction == RIGHT:
        if temp == LEFT:
            return False
    elif direction == LEFT:
        if temp == RIGHT:
            return False
    elif direction == DOWN:
        if temp == UP:
            return False
    return True

# Waiting and key 'Press a key to play'
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGREEN)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    
    # Quit if Press quit key
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)

    # Did not press any key
    if len(keyUpEvents) == 0:
        return None
    # Quit if Press Escape key
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

# Show start screen
def showStartScreen():
    # Font setting
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    # Begining title 1 setting
    titleSurf1 = titleFont.render('Snaky!', True, WHITE, DARKGREEN)
    # Begining title 2 setting
    titleSurf2 = titleFont.render('Snaky!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        # Display 'Press a key to play'
        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame

# Quit or Escape game
def terminate():
    # To quit pygame
    pygame.quit()
    # To exit system
    sys.exit()

# Make random location
def getRandomLocation(worm,list):
    temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while test_not_ok(temp, worm, list):
        temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return temp

def black_random(worm,list,apple):
    temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while black_test_ok(temp, worm, list, apple):
        temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return temp
       
def gold_random(worm,list,apple):
    temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while black_test_ok(temp, worm, list, apple):
        temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return temp

def black_test_ok(temp, worm, list, apple):
    if apple['x'] == temp['x'] and apple['y'] == temp['y']:
        return True
    for body in worm:
        if temp['x'] == body['x'] and temp['y'] == body['y']:
            return True
    for apple in list:
        if temp['x'] == apple['x'] and temp['y'] == apple['y']:
            return True
    return False

def test_not_ok(temp, worm, list):
    for body in worm:
        if temp['x'] == body['x'] and temp['y'] == body['y']:
            return True
    for dark in list:
        if temp['x'] == dark['x'] and temp['y'] == dark['y']:
            return True
    return False

def black_test(list,worm):
    for temp in list:
        if worm[HEAD]['x'] == temp['x'] and worm[HEAD]['y'] == temp['y']:
            # print(temp)
            return # gameover

# Show if player gameover
def showGameOverScreen():
    # Font setting
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    # if gameover, show 'Game'
    gameSurf = gameOverFont.render('Game', True, WHITE)
    # if gameover, show 'Over'
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()

    # text location setting
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)
    # floating location

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    # Show 'Press a key to play'
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
# Show score during game
def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    # floating location
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)

# Create Apple
def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

def drawGold(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    goldRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, GOLD, goldRect)

def drawBlack(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    blackRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, GRAY, blackRect)

def drawList(list):
    temp = []
    for temp in list:
        x = temp['x'] * CELLSIZE
        y = temp['y'] * CELLSIZE
        drawBlack(temp)

# Draw grid in game background
def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
