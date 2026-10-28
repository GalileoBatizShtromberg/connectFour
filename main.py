from cmu_graphics import *
import random
import math

#main system

#helper functions for the actual like logic
#basically surrounding the actual ai and evaluation function


#a bunch of helper functions for how physics and gameplay work
#physics for dropping the pieces, the physics of confetti, of a button


#animation path for just like running all of those physics functions 


# ----------------------------------------------------------------------
# helper functions for the logic AI
# ----------------------------------------------------------------------

def createBoard():
    # 0 means empty, 1 means red, and 2 means yellow.
    return [[0] * 7 for row in range(6)]


def isValidLocation(board, col):
    return 0 <= col < 7 and board[0][col] == 0


def getLowestRow(board, col):
    if not isValidLocation(board, col):
        return None
    for row in range(5, -1, -1):
        if board[row][col] == 0:
            return row


def dropPiece(board, col, player):
    row = getLowestRow(board, col)
    if row is None:
        return -1
    board[row][col] = player
    return row


def getWinningCells(board, player, row, col):
    # start at the last piece and look both ways along each direction.
    for dRow, dCol in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        cells = [(row, col)]
        for sign in [1, -1]:
            r, c = row + sign * dRow, col + sign * dCol
            while (0 <= r < 6 and 0 <= c < 7 and board[r][c] == player):
                cells.append((r, c))
                r += sign * dRow
                c += sign * dCol
        if len(cells) >= 4:
            return cells
    return []


def isWinningMove(board, player, row, col):
    return len(getWinningCells(board, player, row, col)) >= 4


def getValidLocations(board):
    # Checking the middle first makes the search faster and breaks ties nicely.
    return [c for c in [3, 2, 4, 1, 5, 0, 6] if isValidLocation(board, c)]


def copyBoard(board):
    return [row[:] for row in board]



def evaluateWindow(window, player):
    opponent = 3 - player
    good, bad, empty = window.count(player), window.count(opponent), window.count(0)
    score = 0
    if good == 4:
        score += 100
    elif good == 3 and empty == 1:
        score += 8
    elif good == 2 and empty == 2:
        score += 3
    if bad == 3 and empty == 1:
        score -= 12
    return score


def scorePosition(board, player):
    score = 0
    rows = len(board)
    cols = len(board[0])

    #center score
    centerCol = []
    for r in range(rows):
        centerCol.append(board[r][cols // 2])
    score += centerCol.count(player) * 3

    #horiz
    for r in range(rows):
        for c in range(cols - 3):
            window = [board[r][c], board[r][c+1], board[r][c+2], board[r][c+3]]
            score += evaluateWindow(window, player)

    #verticals
    for c in range(cols):
        for r in range(rows - 3):
            window = [board[r][c], board[r+1][c], board[r+2][c], board[r+3][c]]
            score += evaluateWindow(window, player)

    # / pos diag
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r][c], board[r+1][c+1], board[r+2][c+2], board[r+3][c+3]]
            score += evaluateWindow(window, player)

    # \ neg diag
    for r in range(3, rows):
        for c in range(cols - 3):
            window = [board[r][c], board[r-1][c+1], board[r-2][c+2], board[r-3][c+3]]
            score += evaluateWindow(window, player)

    return score

def miniIsWinningMove(board, player, row, col):
        for dRow, dCol in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = 1

            for sign in [1, -1]:
                r = row + sign*dRow
                c = col + sign*dCol

                while (0 <= r < 6 and 0 <= c < 7 and
                    board[r][c] == player):
                    count += 1
                    r += sign*dRow
                    c += sign*dCol

            if count >= 4:
                return True

        return False

#BOOKMARK
def minimax(board, depth, alpha, beta, maxxingPlayer,
            lastRow=-1, lastCol=-1):

    #player 1 is person, 2 is computer
    # returns (col, score, imagined ).
    lastPlayer = 1 if maxxingPlayer else 2

    # if its a winning move in the imagined future end the sequence 
    #returns none because when it calls itself it doesnt want to add a new col it just wants to know that theres a big jackpot there
    if lastRow != -1 and miniIsWinningMove(board, lastPlayer, lastRow, lastCol):
        value = 100000 if lastPlayer == 2 else -100000
        return None, value, []
   
    locations = getValidLocations(board)
    if not locations:
        return None, 0, []
    if depth == 0:
        return None, scorePosition(board, 2), []

    player = 2 if maxxingPlayer else 1
    #I keep track of the player as true(bot) or false(person)
    value = float('-inf') if maxxingPlayer else float('inf')
    bestCol, bestLine = locations[0], []
    for col in locations:
        tempBoard = copyBoard(board)
        row = dropPiece(tempBoard, col, player)
        nextCol, newScore, nextLine = minimax(
            tempBoard, depth - 1, alpha, beta, not maxxingPlayer, row, col)
        better = newScore > value if maxxingPlayer else newScore < value
        if better:
            value, bestCol = newScore, col
            bestLine = [(row, col, player)] + nextLine
        # alpha beta skip branches that arent better
        if maxxingPlayer:
            alpha = max(alpha, value)
        else:
            beta = min(beta, value)
        if alpha >= beta:
            break
    return bestCol, value, bestLine


# ----------------------------------------------------------------------
# 2. SETUP AND GAMEPLAY
# ----------------------------------------------------------------------

def onAppStart(app):
    # settings area
    app.stepsPerSecond = 120
    app.timeScale = 60 / app.stepsPerSecond
    app.dt = 1 / app.stepsPerSecond
    app.dropSpeed0 = 10000
    app.dropGravity = 110000
    app.dropSubSteps = 6          # smaller steps per frame
    app.screen = 'menu'
    app.mode = 'computer'
    app.startPlayer = 1
    app.difficulty = 'challenge'
    app.depths = {'easy': 2, 'challenge': 8}
    app.mouseX, app.mouseY = -1, -1
    app.boardLeft, app.boardTop = 58, 255
    app.cellSize = 76
    app.boardWidth, app.boardHeight = 532, 456
    app.pieceRadius = 29

    #colors
    app.bg = rgb(227, 218, 201)
    app.panel = rgb(200,200,200)
    app.muted = rgb(62, 78, 101)
    app.ink = rgb(90, 90, 90)
    app.accent = rgb(255, 69, 0)
    app.ticks = 0
    app.turnPause = 0

    #check
    app.noticeFrames = rounded(150 / app.timeScale)
    newRound(app)


def newRound(app):

    # temporary initializations per round
    app.board = createBoard()
    app.turn = app.startPlayer
    app.history = []                 # (row, col, player) for every landed chip
    app.falling = None               # a dictionary only while a chip is falling
    app.gameOver = False
    app.winner = None
    app.winningCells = []
    app.confetti = []
    app.aiWait = app.turnPause       # give the player a moment to see whose turn it is
    app.aiPlan = []
    app.showPlan = False
    app.selectedCol = 3
    app.notice = ''
    app.noticeTimer = 0


def getCellCenter(app, row, col):
    return (app.boardLeft + (col + 0.5) * app.cellSize,
            app.boardTop + (row + 0.5) * app.cellSize)


def playerName(app, player):
    if app.mode == 'computer':
        return 'You' if player == 1 else 'Computer'
    return 'Red' if player == 1 else 'Yellow'


def humanTurn(app):
    return app.mode == 'friends' or app.turn == 1


def showNotice(app, text):
    app.notice, app.noticeTimer = text, app.noticeFrames


def startDrop(app, col):
    # computer and humans all use this one animation function
    if app.gameOver or app.falling is not None:
        return
    row = getLowestRow(app.board, col)
    if row is None:
        showNotice(app, 'That column is full. Try another!')
        return
    cx, targetY = getCellCenter(app, row, col)
    startY = app.boardTop - 100
    # prevY is where the chip was on the previous frame. The drawing code uses
    # it to sketch a short trail, which reads as motion blur at high speed.
    app.falling = {'row': row, 'col': col, 'player': app.turn,
                   'y': startY, 'prevY': startY, 'targetY': targetY,
                   'speed': app.dropSpeed0}

    #empties the stuff because it no longer exists, 
    # and cuts off the notice so its not there as it drops
    app.aiPlan = []
    app.noticeTimer = 0


#just checks if it is win, tie, continue 
def finishDrop(app):
    piece = app.falling
    row, col, player = piece['row'], piece['col'], piece['player']
    app.board[row][col] = player
    app.history.append((row, col, player))
    app.falling = None
    app.winningCells = getWinningCells(app.board, player, row, col)
    if app.winningCells:
        app.gameOver, app.winner = True, player
        #  celebrate win, including either person in two-player mode.
        if app.mode == 'friends' or player == 1:
            makeConfetti(app)
    elif not getValidLocations(app.board):
        app.gameOver, app.winner = True, 'Tie'
    else:
        app.turn = 3 - player # 3-1 or 3-2 is 2 or 1
        app.aiWait = app.turnPause

#BOOKMARK
def undoMove(app):
    # cancel any unfinished drop first; it has not reached the board yet.
    pending = app.falling
    # but keep the pending 
    app.falling = None
    if app.mode == 'friends':
        # iff a person pressed undo while its falling , just cancel that drop 
        if pending is None and app.history:
            row, col, player = app.history.pop()
            app.board[row][col] = 0
            app.turn = player
    else:
        # undo through the most recent human move and the ai reply so it doesnt just go again
        humanIndex = None
        for i in range(len(app.history) - 1, -1, -1):
            if app.history[i][2] == 1:
                humanIndex = i
                break
        if pending is not None and pending['player'] == 1:
            # if they press while its falling
            app.turn = 1
        elif humanIndex is not None:
            #remove stuff till you get to the index 
            while len(app.history) > humanIndex:
                row, col, player = app.history.pop()
                app.board[row][col] = 0
            app.turn = 1
        else:
            #this just does nothing 
            showNotice(app, 'No completed turn to undo yet.')
    app.gameOver = False
    app.winner = None
    app.winningCells = []
    app.confetti = []
    app.aiPlan = []
    app.aiWait = app.turnPause


def makeConfetti(app):
    app.confetti = []
    for i in range(180):
        app.confetti.append({
            'x': random.randint(20, app.width - 20),
            'y': random.randint(-100, -10),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(6, 12),
            'angle': random.randint(0, 360),
            'spin': random.uniform(-5, 5),
            'color': 'salmon' if app.history[-1][-1] == 1 else "gold"})


# ----------------------------------------------------------------------
# 3. INPUT AND ANIMATION
# ----------------------------------------------------------------------

def inside(x, y, left, top, width, height):
    return left <= x < left + width and top <= y < top + height


def columnAt(app, x, y):
    #kinda obvious but still returns the column right above
    if inside(x, y, app.boardLeft, app.boardTop - 65,
              app.boardWidth, app.boardHeight + 65):
        return int((x - app.boardLeft) // app.cellSize)
    return None


def onMouseMove(app, mouseX, mouseY):
    #makes the column what the mouse is hovering over (initialized to middle)
    app.mouseX, app.mouseY = mouseX, mouseY
    if app.screen == 'game':
        col = columnAt(app, mouseX, mouseY)
        if col is not None:
            app.selectedCol = col


def onMousePress(app, mouseX, mouseY):
    app.mouseX, app.mouseY = mouseX, mouseY
    if app.screen == 'menu':
        # so this is like the menu part where if you are hovering over that thing 
        if inside(mouseX, mouseY, 110, 270, 325, 95):
            app.mode = 'computer'
        elif inside(mouseX, mouseY, 465, 270, 325, 95):
            app.mode = 'friends'
        elif inside(mouseX, mouseY, 110, 423, 325, 64):
            app.startPlayer = 1
        elif inside(mouseX, mouseY, 465, 423, 325, 64):
            app.startPlayer = 2
        elif app.mode == 'computer' and 540 <= mouseY < 594:
            #just like runs as that instead of putting two more 
            for i, name in enumerate(['easy', 'challenge']):
                if inside(mouseX, mouseY, 225 + i * 235, 540, 210, 54):
                    app.difficulty = name
        elif inside(mouseX, mouseY, 260, 650, 380, 65):
            newRound(app)
            app.screen = 'game'
        #this return is important so that the other boxes dont get checked
        return

        #while in menut ^^^
        #while in game vvv

    if inside(mouseX, mouseY, 636, 380, 210, 48):
        undoMove(app)
    elif inside(mouseX, mouseY, 636, 444, 210, 48):
        newRound(app)
    elif inside(mouseX, mouseY, 636, 508, 210, 48):
        app.screen = 'menu'
    elif app.mode == 'computer' and inside(mouseX, mouseY, 636, 572, 210, 48):
        app.showPlan = not app.showPlan
    elif humanTurn(app):
        col = columnAt(app, mouseX, mouseY)
        if col is not None:
            app.selectedCol = col
            startDrop(app, col)


def onKeyPress(app, key):
    #keybinds obviously
    if app.screen == 'menu':
        if key in ['enter', 'space']:
            newRound(app)
            app.screen = 'game'
        return
    if key == 'u':
        undoMove(app)
    elif key == 'r':
        newRound(app)
    elif key == 'm':
        app.screen = 'menu'
    elif key == 'p' and app.mode == 'computer':
        app.showPlan = not app.showPlan
    elif humanTurn(app) and not app.gameOver and app.falling is None:
        if key == 'left':
            app.selectedCol = (app.selectedCol - 1) % 7
        elif key == 'right':
            app.selectedCol = (app.selectedCol + 1) % 7
        elif key in ['space', 'enter']:
            startDrop(app, app.selectedCol)
        elif key in ['1', '2', '3', '4', '5', '6', '7']:
            app.selectedCol = int(key) - 1
            startDrop(app, app.selectedCol)


#BOOKMARK


def onStep(app):
    # so like nothing during the menu 
    if app.screen != 'game':
        return
    app.ticks += 1
    if app.noticeTimer > 0:
        app.noticeTimer -= 1

    # confetti runs no matter whose turn it is.
    

    remaining = []
    scale = app.timeScale
    for piece in app.confetti:
        piece['x'] += piece['vx'] * scale
        piece['y'] += piece['vy'] * scale
        piece['vy'] += 0.025 * scale
        piece['angle'] += piece['spin'] * scale
        if piece['y'] < app.height + 20:
            remaining.append(piece)
    app.confetti = remaining

    
    if app.falling is not None:
        piece = app.falling
        piece['prevY'] = piece['y']
        
        #step is time and you get 6 in a frame
        step = app.dt / app.dropSubSteps
        for i in range(app.dropSubSteps):
            #speed timesequals grav and y plusequals speed
            piece['speed'] += app.dropGravity * step
            piece['y'] += piece['speed'] * step

            if piece['y'] >= piece['targetY']:
                # land exactly in the slot instead of a pixel or two past it
                piece['y'] = piece['targetY']
                break
        if piece['y'] >= piece['targetY']:
            finishDrop(app)
        return

        #right stiutation(mode, turn) means it just runs the alg then drops, and waits if you have that setting, i have it to zero
    if not app.gameOver and app.mode == 'computer' and app.turn == 2:
        if app.aiWait > 0:
            app.aiWait -= 1
        else:
            col, score, line = minimax(app.board, app.depths[app.difficulty],
                                       float('-inf'), float('inf'), True)
            if col is not None:
                startDrop(app, col)
                app.aiPlan = line


# ----------------------------------------------------------------------
# draw (drawing functions never change the game)
# ----------------------------------------------------------------------

def roundedRect(left, top, width, height, radius, color, opacity=100):
    # cmu graphics rectangles have square corners so two rectangles and four circles make a rounded panel without needing another library.
    drawRect(left + radius, top, width - 2 * radius, height,
             fill=color, opacity=opacity)
    drawRect(left, top + radius, width, height - 2 * radius,
             fill=color, opacity=opacity)
    for x in [left + radius, left + width - radius]:
        for y in [top + radius, top + height - radius]:
            drawCircle(x, y, radius, fill=color, opacity=opacity)


def drawButton(app, text, left, top, width, height,
               selected=False, primary=False, subtitle=None):
    hovered = inside(app.mouseX, app.mouseY, left, top, width, height)
    edge = app.accent if selected or primary else rgb(100, 100, 91)
    fill = rgb(200, 90, 0) if hovered else app.panel

    # primary is just for the play button later cuz everything else is normal
    if primary:
        fill = app.accent
        
    roundedRect(left, top, width, height, 13, edge)
    roundedRect(left + 2, top + 2, width - 4, height - 4, 11, fill)
    color = app.bg if primary else app.ink
    # label at center y
    cy = top + height / 2 if subtitle is None else top + 32
    drawLabel(text, left + width / 2, cy, size=17, bold=True, fill=color)
    if subtitle is not None:
        drawLabel(subtitle, left + width / 2, top + 63,
                  size=12, fill=app.muted)


#again red is one yellow is two
def getPlayerColor(player):
    return rgb(255, 119, 125) if player == 1 else rgb(255, 206, 94)


#opacity is important for the motion blur
def drawChip(app, x, y, player, radius=None, opacity=100):
    if radius is None:
        radius = app.pieceRadius
    drawCircle(x, y + 3, radius, fill=rgb(8, 14, 26), opacity=opacity)
    drawCircle(x, y, radius, fill=getPlayerColor(player), opacity=opacity)
    drawCircle(x, y, radius - 5, fill=None, border=app.bg,
               borderWidth=1.5, opacity=opacity * 0.18)
    drawOval(x - radius * 0.24, y - radius * 0.36,
             radius * 0.7, radius * 0.28, fill='white', opacity=opacity * 0.25)


def drawBackground(app):
    drawRect(0, 0, app.width, app.height, fill=app.bg)

#menut is kinda simple its just the things
def drawMenu(app):
    for i, player in enumerate([1, 2, 1, 2]):
        drawChip(app, 396 + i * 36, 76, player, 12)
    drawLabel('CONNECT FOUR ENGINE', 450, 135, size=39, bold=True, fill=app.ink)
    drawLabel('You can play a bot that I made or play somebody else',
              450, 184, size=16, fill=app.muted)
    drawButton(app, 'play the engine', 110, 270, 325, 95,
               selected=app.mode == 'computer', subtitle='it is hard to beat, but doable')
    drawButton(app, 'play locally', 465, 270, 325, 95,
               selected=app.mode == 'friends', subtitle='for two people on one computer')
    first = 'you go first' if app.mode == 'computer' else 'red goes first'
    second = 'you go second' if app.mode == 'computer' else 'yellow goes first'
    drawButton(app, first, 110, 423, 325, 64, selected=app.startPlayer == 1)
    drawButton(app, second, 465, 423, 325, 64, selected=app.startPlayer == 2)
    if app.mode == 'computer':
        for i, name in enumerate(['easy', 'challenge']):
            drawButton(app, name, 225 + i * 235, 540, 210, 54,
                       selected=app.difficulty == name)
    drawButton(app, "play", 260, 650, 380, 65, primary=True)
    drawLabel('Dont let it catch you off guard',
              450, 754, size=13, fill=app.muted)

#also obviously the little message for in game
def getStatusMessage(app):
    if app.winner == 'Tie':
        return 'A perfect stalemate.'
    if app.gameOver:
        if app.mode == 'computer' and app.winner == 1:
            return 'You win!' 
        else:
            return f'{playerName(app, app.winner)} wins!'
    if app.falling is not None:
        return 'Here comes your chip...' if humanTurn(app) else 'Here comes the reply...'
    if not humanTurn(app):
        return 'Computer is thinking...'
    return 'Your turn.' if app.mode == 'computer' else f'{playerName(app, app.turn)}\'s turn.'

# mind blowing 
def drawBoard(app):
    left, top = app.boardLeft, app.boardTop
    roundedRect(left - 12, top + 7, app.boardWidth + 24,
                app.boardHeight + 24, 23, rgb(8, 14, 26))
    roundedRect(left - 12, top - 12, app.boardWidth + 24,
                app.boardHeight + 24, 23, rgb(57, 79, 112))
    roundedRect(left - 7, top - 7, app.boardWidth + 14,
                app.boardHeight + 14, 19, rgb(41, 61, 89))
    for row in range(6):
        for col in range(7):
            x, y = getCellCenter(app, row, col)
            drawCircle(x, y, app.pieceRadius + 3, fill=rgb(21, 34, 54))
            drawCircle(x, y + 2, app.pieceRadius, fill=app.bg)
            player = app.board[row][col]
            if player != 0:
                drawChip(app, x, y, player)
            if (row, col) in app.winningCells:
                pulse = 65 + 25 * math.sin(app.ticks * app.timeScale / 9)
                drawCircle(x, y, app.pieceRadius + 4, fill=None,
                           border='white', borderWidth=3, opacity=pulse)
    # a small dot marks the last completed move
    if app.history:
        row, col, player = app.history[-1]
        x, y = getCellCenter(app, row, col)
        drawCircle(x, y + 13, 3, fill=app.bg, opacity=70)

    #if plan toggled it gets the inputs from the ai plan and just draws the chips 
    if app.showPlan and not app.gameOver and app.falling is None:
        for i, (row, col, player) in enumerate(app.aiPlan[1:]):
            if app.board[row][col] == 0:
                x, y = getCellCenter(app, row, col)
                drawCircle(x, y, 22, fill=getPlayerColor(player), opacity=23)
                drawLabel(str(i + 1), x, y, size=13, fill=app.ink)
    
    # next is either the falling chip or the hovering preview
    # its either drawing the falling pieces as having slightly behind for motion blur
    if app.falling is not None:
        piece = app.falling
        x, targetY = getCellCenter(app, piece['row'], piece['col'])
        gap = piece['y'] - piece['prevY']
        if gap > 6:
            for i in range(1, 4):
                ghostY = piece['prevY'] + gap * i / 4
                if ghostY > app.boardTop - 60:
                    drawChip(app, x, ghostY, piece['player'],
                             app.pieceRadius - 2, opacity=16 * i)
        drawChip(app, x, piece['y'], piece['player'])

    #falling ^^^
    #hovering vvv


    #or not drawing any pieces at all and putting the lil token above the board
    elif not app.gameOver and humanTurn(app):
        col = app.selectedCol
        x, y = getCellCenter(app, 0, col)
        if isValidLocation(app.board, col):
            row = getLowestRow(app.board, col)
            gx, gy = getCellCenter(app, row, col)
            drawCircle(gx, gy, app.pieceRadius - 3,
                       fill=getPlayerColor(app.turn), opacity=18)
            drawChip(app, x, top - 42, app.turn, 23)
        else:
            drawLabel('FULL', x, top - 42, size=12, bold=True, fill=app.muted)
    
    #these are barely visible but show the column numbers 
    for col in range(7):
        x, y = getCellCenter(app, 0, col)
        drawLabel(str(col + 1), x, 740, size=12, fill=app.accent)

#literally draws the sidebar, very simple if you look line by line even though it looks dense
def drawSidebar(app):
    roundedRect(620, 200, 242, 525, 20, app.panel)
    drawLabel('THE MATCH', 640, 232, align='left', size=12,
              bold=True, fill=app.accent)
    for player in [1, 2]:
        y = 279 + (player - 1) * 60
        drawChip(app, 660, y, player, 16)
        drawLabel(playerName(app, player), 690, y - 7, align='left',
                  size=17, bold=True, fill=app.ink)
        subtitle = 'Red chips' if player == 1 else 'Yellow chips'
        if player == 2 and app.mode == 'computer':
            subtitle = app.difficulty + ' difficulty'
        drawLabel(subtitle, 690, y + 15, align='left', size=11, fill=app.muted)
        if player == app.turn and not app.gameOver:
            drawCircle(840, y, 4, fill=app.accent)
    drawButton(app, 'Undo   [U]', 636, 380, 210, 48)
    drawButton(app, 'New round   [R]', 636, 444, 210, 48)
    drawButton(app, 'Menu   [M]', 636, 508, 210, 48)
    if app.mode == 'computer':
        text = 'Hide Engine   [P]' if app.showPlan else 'Show Engine  [P]'
        drawButton(app, text, 636, 572, 210, 48, selected=app.showPlan)
        drawLabel('not a guaranteed future.', 741, 641,
                  size=10, fill=app.muted)
    drawLabel(f'{len(app.history)} chips played', 741, 690,
              size=13, fill=app.muted)


#every frame, does not modify nothin, only runs the screen 
def redrawAll(app):
    #background, menu end it for that moment
    drawBackground(app)
    if app.screen == 'menu':
        drawMenu(app)
        return

    # if it doesnt get killed by menuness it does all the other stuff
    drawLabel('Connect Four', 46, 51, align='left', size=30,
              bold=True, fill=app.ink)
    label = 'WITH A FRIEND' if app.mode == 'friends' else 'VS ENGINE'
    drawLabel(label, 850, 51, align='right', size=12, bold=True, fill=app.accent)
    drawLabel(getStatusMessage(app), 46, 115, align='left', size=26,
              bold=True, fill=app.ink)
    hint = 'you know the rules'
    if app.gameOver:
        hint = 'R for a rematch, or U to undo.'
    if app.noticeTimer > 0:
        hint = app.notice
    drawLabel(hint, 46, 153, align='left', size=14, fill=app.muted)
    drawBoard(app)
    drawSidebar(app)
    drawLabel('Click or 1-7 to drop  /  Arrow keys + Space  /  U to undo',
              450, 780, size=12, fill=app.muted)

    #so usually theres nothing in this list but when there is it makes it spin
    for piece in app.confetti:
        drawRect(piece['x'], piece['y'], 8, 4, fill=piece['color'],
                 rotateAngle=piece['angle'])

# this is like obiously to run the app
def main():
    runApp(width=900, height=810)

#only runs when I want to run instead of if its importing. 
#I understand what it does but this was AI's idea. 
if __name__ == '__main__':
    main()
