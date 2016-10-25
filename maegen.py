from EaselLib import *
from random import choice
from math import sqrt
import sqlite3
from pygame.transform import scale

'''
MAEGEN:

Note: Functions that read data from the game state will have "readState"
included as an argument in their signatures. Similarly, functions that
alter the game state or read input will respectively have "writeState" and
"readInput" in their signatures.

Uses the game rules and definitions specified in "Maegen Rules" and
"Maegen ASM" in addition to the following:

A *coded cell* is a triple (C, f, g), where C is a cell and f and g are
real numbers

Let U be a unit on the board. The *sprite for U* is defined as follows:
    If U is a swordsman, the sprite for U is a list of line segments forming
        an "X" shape, centered in U's cell and 60 * 60 pixels in dimensions.
        The images are colored a faded black if U has acted this phase, green
        if U is selected, and black otherwise. Such a list of images
        may be referred to as a *swordsman sprite*.
        If U is a slinger, the sprite for U is a list of images whose only
        member is a circle centered in U's cell and 30 pixels in radius.
        The image is colored a faded red if U has acted this phase, green
        if U is selected, and red otherwise. Such a list of images may
        be referred to as a "slinger sprite".


Additional specs:


The game window will be 800 pixels * 1000 pixels.

The game will be played on a 10 * 10 grid of 60 pixel * 60 pixel cells,
centered horizontally in the game window and whose upper edge is 50 pixels
from the top of the game window.

During movement and attack phases, units are selected by game-clicking the cell
they are in. *Game-clicking* a space means moving the left mouse button
from up to down while the cursor is in that space.

Selected units are displayed in green

Once a unit is selected, the action corresponding to that unit, the
current player, and the current phase is either executed or aborted
(based on the requirements of that action) by game-clicking a target cell.

selected is a global variable that holds the index of a unit, or None.
It is initialized to None.

The background of the game is a very light grey.

Units that have acted in the current move/attack phase are lighter than their
counterparts. That is, their colors are closer to the background color.

Two buttons, referred to as button 1 and button 2, are depicted in various
phases of the game.

Buttons are 60 pixels * 60 pixels.

Button 1 is displayed only before the first deployment. Button 2 is displayed
whenever the game is not in a deployment phase.

The center of each button is 175 pixels from the bottom of the screen.

Button 1 is horizontally centered in the left half of the screen, while button
2 is horizontally centered in the right half.

Clicking button 1 during the call toss phase calls "heads", adding
CoinToss("head") to the action queue. Clicking button 1 during the "selectFirst"
phase selects red to go first.

Clicking button 2 during the call toss phase calls "tails", adding
CoinToss("tail") to the action queue. Clicking button 2 during the "selectFirst"
phase selects black to go first. Clicking button 2 during any other
non-deployment phase (except "gameOver") adds all of the current
player's active units to the list of acted units (i.e. "passes" the turn).

'''


#==============
'''Constants'''
#==============

# windowDimensions: int * int
# windowDimensions() is (800,1000).
# first return value: number of pixels wide
# second return value: number of pixels high
def windowDimensions():
    return (533,666)

# otherPlayer: player -> player
# otherPlayer(S) is "black" if S is "red" and "red" otherwise.
def otherPlayer(S):
    if S == "red":
        return "black"
    return "black"

# mapDimensions: int * int
# mapDimensions() is (10,10)
# the game will not function if the two return values are different
def mapDimensions(): return (10,10)

# cellWidth: int
# cellWidth() is 60.
def cellWidth():
    return windowDimensions()[0]/13.333

# buttonDimensions: int * int
# buttonDimensions() is (60,60)
def buttonDimensions():
    return (windowDimensions()[0]/13.333,windowDimensions()[0]/13.333)

# verticalOffset: int
# verticalOffset() is 150.
# game will not function if changed
def verticalOffset():
    return windowDimensions()[1]/6.666

# button1Area: Rectangle
# button1Area() is an x * y rectangle with its top-left corner at (-230,-295),
# where (x,y) is buttonDimensions().
def button1Area():
    return Rectangle(windowDimensions()[0]/-3.478, windowDimensions()[1]/-3.39, buttonDimensions()[0], buttonDimensions()[1])

# button2Area: Rectangle
# button2Area() is an x * y rectangle with its top-left corner at (170,-295),
# where (x,y) is buttonDimensions().
def button2Area():
    return Rectangle(windowDimensions()[0]/4.706, windowDimensions()[1]/-3.39, buttonDimensions()[0], buttonDimensions()[1])

# board: Rectangle
# board() is an h*w Rectangle with its center point at (0, verticalOffset()),
# where h is the number of columns on the board times the cell width and w is
# the number of rows on the board times the cell width.
def board():
    columns = mapDimensions()[0]
    rows = mapDimensions()[1]
    left = columns/2 * -1 * cellWidth()
    top = rows/2 * cellWidth() + verticalOffset()
    w = columns * cellWidth()
    h = rows * cellWidth()
    b = Rectangle(left,top,w,h)
    return b




















#============
'''Classes'''
#============

# As pygame uses an inverted y axis for class Rect, it was easiest to write
# my own Rectangle class:
# A Rectangle is an object R with fields left, top, width, and height,
# where all fields of R are integers, (left,top) represents the top-left
# corner of a rectangle on a cartesian plane, and width and height represent
# the respective width and height of such a rectangle, in pixels.
class Rectangle:

    # __init__: writeState
    # If self is a Rectangle and x, y, w, and h are integers, then
    # __init__(self, x, y, w, h) sets the left, top, width, and height fields
    # of self to x, y, w, and h, respectively.
    def __init__(self, x, y, w, h):
        self.left = x
        self.top = y
        self.width = w
        self.height = h

    # If self is a Rectangle and p is a point, containsPoint(self, p) iff
    # p is a point inside the rectangle represented by self (i.e.
    # self.left <= p[0] < self.left + self.width and
    # self.top >= p[1] > self.top - self.height.)
    def containsPoint(self, p):
        (x,y) = p
        r1 = self.left <= x and x < self.left + self.width
        r2 = self.top >= y and y > self.top - self.height
        return r1 and r2

# A Unit is an object as defined in the Maegen architecture/game model, with
# the exception that the field "range" has been renamed to "unitRange."
class Unit:

    # __init__: Unit -> writeState
    # If self is a Unit, __init__(self) sets self's index, movement, and
    # unitRange to 0 and sets its hitRoll, armor, and damage to 1.
    # (included because the class can't be empty.)
    def __init__(self):
        self.index = 0
        self.movement = 0
        self.unitRange = 0
        self.hitRoll = 1
        self.armor = 1
        self.damage = 1

# A Slinger is a Unit whose fields are those of a slinger as
# defined in the Maegen rules.
class Slinger(Unit):

    # __init__: Swordsman * int -> writeState
    # If self is a Slinger and idx is an integer, then __init__(self,idx)
    # sets self.index to idx and the other fields of self to match the
    # attributes of a slinger, as defined in the game rules.
    def __init__(self, idx):
        s = getStats()['slinger']
        self.index = idx
        self.movement = s[0]
        self.unitRange = s[1]
        self.hitRoll = s[2]
        self.armor = s[3]
        self.damage = s[4]

# A Swordsman is a Unit whose fields are those of a swordsman as
# defined in the Maegen rules.
class Swordsman(Unit):

    # __init__: Swordsman * int -> writeState
    # If self is a Swordsman and idx is an integer, then __init__(self,idx)
    # sets self.index to idx and the other fields of self to match the
    # attributes of a swordsman, as defined in the game rules.
    def __init__(self, idx):
        s = getStats()['swordsman']
        self.index = idx
        self.movement = s[0]
        self.unitRange = s[1]
        self.hitRoll = s[2]
        self.armor = s[3]
        self.damage = s[4]

# PlayerAction is an abstract class with the following virtual functions:
#
# reqs: PlayerAction * readState -> bool
# reqs(self) reads the game state and returns true if the requirements for
# PlayerAction self, as defined in the game architecture, are met.
#
# effects: PlayerAction -> writeState
# effects(self) modifies the game state to reflect the effects of
# PlayerAction self, as defined in the game architecture.
class PlayerAction:

    # __init__: PlayerAction -> PlayerAction
    # __init__(self) returns self.
    # (ideally, this method wouldn't exist, but I can't have the
    # class be empty, and a "blank" player action would have no attributes.)
    def __init__(self):
        return self


# CoinToss(s): "red" calls the toss as coin-side s.
class CoinToss(PlayerAction):

    # __init__: CoinToss * coin-side -> writeState
    # If call is a coin-side and self is a CoinToss, __init__(self, call)
    # sets self's s field to call.
    def __init__(self, call):
        self.s = call;

    # reqs: CoinToss * readState -> bool
    # reqs(self) iff the game's control state is "callToss".
    def reqs(self):
        return getCtrl() == "callToss"

    # effects: CoinToss -> writeState
    # effects(self) selects a random coin-side. If the result equals s, then
    # effects(self) sets the tossWinner to red. Otherwise, effects(self) sets the
    # tossWinner to black.
    # After the above, effects(self) sets ctrl to selectFirst.
    def effects(self):
        result = coinResult()
        if result == self.s:
            setTossWinner("red")
        else:
            setTossWinner("black")
        setCtrl("selectFirst")

# SelectFirstPlayer(p,q) -- player p selects player q to deploy first.
class SelectFirstPlayer(PlayerAction):

    # __init__: SelectFirstPlayer * player * player -> writeState
    # If p1 and q2 are players and self is a SelectFirstPlayer,
    # __init__(self, p1, q2) sets self's p and q members to p1 and q2,
    # respectively.
    def __init__(self, p1, q2):
        self.p = p1
        self.q = q2

    # reqs: SelectFirstPlayer * readState -> bool
    # reqs() iff the game's control state is selectFirst and p is the
    # tossWinner.
    def reqs(self):
        return getCtrl() == "selectFirst" and self.p == getTossWinner()

    # effects: SelectFirstPlayer -> writeState
    # If self is a SelectFirstPlayer, effects(self) sets firstPlayer to self.q,
    # secondPlayer to otherPlayer(self.q), and the control state to
    # ("deploy", self.q).
    def effects(self):
        setFirstPlayer(self.q)
        setSecondPlayer(otherPlayer(self.q))
        setCtrl(("deploy", self.q))

# Place(p,u,A) -- player p places unit u in cell A.
class Place(PlayerAction):

    # __init__: Place * player * unit * Cell -> writeState (?)
    # if self is a Place, pl is a player, un is a unit, and C is a cell,
    # __init__(self, pl, un, C) sets self's p, u, and A fields to
    # respective values pl, un, and C.
    def __init__(self, player, unit, Cell):
        self.p = player
        self.u = unit
        self.A = Cell

    # reqs: Place * readState -> bool
    # If self is a Place, reqs(self) iff the following:
    #   The control state is ("deploy", self.p).
    #   Unit self.u's index is in player army(self.p), where self.p is
    #       a player.
    #   Unit self.u is not on the board.
    #   Cell self.A is unoccupied.
    def reqs(self):
        r1 = getCtrl() == ("deploy", self.p)
        r2 = self.u.index in army(self.p)
        r3 = not onBoard(self.u)
        r4 = not occupied(self.A)
        return r1 and r2 and r3 and r4

    # effects: Place -> writeState
    # If self is a Place, effects(self) sets the location of self.u to self.A.
    def effects(self):
        setLocation(self.u, self.A)

# Move(p,u,B) -- player p moves unit u to cell B
class Move(PlayerAction):

    # __init__: Move * player * unit * cell -> writeState
    # If self is a Move, pl is a player, un is a unit, and C is a cell,
    # __init__(self, pl, un, C) sets self's p, u, and B fields to respective values
    # pl, un, and C.
    def __init__(self, player, unit, Cell):
        self.p = player
        self.u = unit
        self.B = Cell

    # reqs: Move * readState -> bool
    # If self is a Move, reqs(self) iff the following:
    #   The control state is ("move", self.p).
    #   Unit self.u's index is in player army(self.p), where self.p is
    #       a player.
    #   Unit self.u is on the board.
    #   Unit self.u has not yet acted in the current phase.
    #   Cell self.B is unoccupied.
    #   The movement cost from unit self.u's location to cell self.B is less
    #       than or equal to self.u's movement stat.
    def reqs(self):
        r1 = getCtrl() == ("move", self.p)
        r2 = self.u.index in army(self.p)
        r3 = onBoard(self.u)
        r4 = not (self.u.index in getActed())
        r5 = not occupied(self.B)
        r6 = moveCost(unitLocation(self.u), self.B) <= movement(self.u)
        return r1 and r2 and r3 and r4 and r5 and r6

    # effects: Move -> writeState
    # If self is a Move, effects(self) sets the location of self.u to
    # self.B, then sets acted to acted | {self.u.index}.
    def effects(self):
        setLocation(self.u, self.B)
        setActed(getActed() | {self.u.index})
        if currentPlayer() == "red":
            playSound(Slinger_Move)
        else:
            playSound(Swordsman_Move)

# Attack(p,u,v): player p's unit u attacks unit v.
class Attack(PlayerAction):

    # __init__: Attack * player * unit * unit -> writeState
    # if self is an Attack, pl is a player, and a and b are units,
    # __init__(self, pl, a, b) sets self's p, u, and v fields to respective
    # values pl, a, and b.
    def __init__(self, player, unit1, target):
        self.p = player
        self.u = unit1
        self.v = target

    # reqs: Attack * readState -> bool
    # If self is an Attack, reqs(self) iff the following:
    #   The control state is ("attack", self.p).
    #   Unit self.u's index is in player self.p's army.
    #   Unit self.u is on the board.
    #   Unit self.u has not yet acted in the current phase.
    #   The straight-line distance from self.u's location to self.v's location
    #       is less than or equal to self.u's range.
    #   There is a clear line of attack from self.u's location to self.v's
    #       location.
    def reqs(self):
        l1 = unitLocation(self.u)
        l2 = unitLocation(self.v)
        # requirements
        r1 = getCtrl() == ("attack", self.p)
        r2 = self.u.index in army(self.p)
        r3 = onBoard(self.u)
        r4 = not(self.u.index in getActed())
        r5 = straightLineDistance(l1, l2) <= unitRange(self.u)
        r6 = clearLineOfAttack(l1, l2)
        return r1 and r2 and r3 and r4 and r5 and r6

    # effects: Attack
    # effects(self) simulates three six-sided dice rolls. If the first is less
    # than or equal to the hitRoll of self.u, the second is less than or equal
    # to the armor of self.v, and the last is less than or equal to the damage
    # of self.u, then effects(self) removes v from the board.
    # After the above, effects(self) adds self.u's index to acted.
    def effects(self):
        if attackRoll() <= hitRoll(self.u):
            if armorRoll() <= armor(self.v):
                if damageRoll() <= damage(self.u):
                    setLocation(self.v, None)
                    if currentPlayer() == "red":
                        playSound(Swordsman_Die)
                    else:
                        playSound(Slinger_Die)
        setActed(getActed() | {self.u.index})
        if currentPlayer() == "red":
            playSound(Slinger_Attack)
        else:
            playSound(Swordsman_Attack)




















#============================
'''Functions and Relations'''
#============================

# onBoard: unit * readState -> bool
# If u is a unit, onBoard(u) iff the location of u is not None.
def onBoard(u):
    return not unitLocation(u) == None

# occupied: cell * readState -> bool
# If A is a cell, occupied(A) iff there is a unit whose location is A.
def occupied(A):
    for u in getRoster():
        if unitLocation(u) == A:
            return True
    return False

# coinResult: coin-side
# coinResult() is "head" or "tail", chosen at random.
def coinResult():
    return choice(["head", "tail"])

# attackRoll: int
# attackRoll() is an integer in {1..6}, chosen at random.
def attackRoll():
    return choice(range(1,7))

# damageRoll: int
# damageRoll() is an integer in {1..6}, chosen at random.
def damageRoll():
    return choice(range(1,7))

# armroRoll: int
# armorRoll() is an integer in {1..6}, chosen at random.
def armorRoll():
    return choice(range(1,7))

# moveCost: cell * cell * readState -> R
# if A and B are cells, then moveCost(A,B) is the cost of a shortest path
# from A to B. If no such path exists, moveCost(A,B) is over nine thousand.
def moveCost(A,B):
    cost = aStar(A,B)[2]
    if cost != -1:
        return cost
    return 9000.1

# aStar: cell * cell * readState -> path * R * R
# aStar implements the A* algorithm.
# If a and b are tiles such that a does not equal b,
# then if there is a traversable path from a to b,
# aStar(a,b) is (p, f, f), where p is the shortest traversable path from
# a to b, and f is the path length of p.
# If there is no traversable path from a to b, aStar(a,b) is ([],-1,-1).
def aStar(a,b):
    if occupied(b): return ([],-1,-1)
    openList = [([a], 0, 0)]
    closedList = []
    while len(openList) > 0:
        q = minF(openList)
        curPath = q[0]
        lastCell = q[0][len(q[0])-1]
        curDist = q[1]
        openList.remove(q)
        edges = (edgeAdjacents(lastCell), 1.0)
        diags = (diagAdjacents(lastCell), 1.5)

        for a in [edges, diags]:
            adjs = a[0]
            dist = a[1]
            for s in adjs:
                T = (curPath+[s], curDist+dist, curDist+dist+cellDist(s,b))
                if s==b:
                    return T
                if not (lowerF(openList, T) or lowerF(closedList,T)):
                    openList += [T]
        closedList += [q]
    return ([],-1,-1)

# cellDist: cell * cell -> R
# If C1 and C2 are cells, cellDist(C1, C2) is the cost of the shortest
# path (occupied or not) between C1 and C2.
def cellDist(C1, C2):
    xMax = max({C1[0], C2[0]})
    yMax = max({C1[1], C2[1]})
    xMin = min({C1[0], C2[0]})
    yMin = min({C1[1], C2[1]})
    count = 0.0
    while (xMax != xMin and yMax != yMin):
        xMax -= 1
        yMax -= 1
        count += 1.5
    count += (xMax - xMin) + (yMax - yMin)
    return count

# edgeAdjacents: cell * readState -> list(cell)
# If c is a cell, then edgeAdjacents(c) is the list of unoccupied
# cells which are edge-adjacent to c.
def edgeAdjacents(c):
    out = []
    for i in {(0,1),(1,0),(-1,0),(0,-1)}:
        n = pairAdd(i, c)
        if validCell(n) and not occupied(n):
            out += [n]
    return out

# diagAdjacents: cell * readState -> cell*
# If c is a cell, then diagAdjacents(c) is the list of unoccupied cells
# which are diagonally adjacent to c.
def diagAdjacents(c):
    out = []
    for i in {(1,1),(1,-1),(-1,1),(-1,-1)}:
        n = pairAdd(i, c)
        if validCell(n) and not occupied(n):
            out += [n]
    return out

# validCell: int * int -> bool
# If C is a pair of integers, validCell(C) iff C is a cell.
def validCell(C):
    (x,y) = C
    t1 = 1 <= x and x <= 10
    t2 = 1 <= y and y <= 10
    return t1 and t2

# pairAdd: (R * R) * (R * R) -> R * R
# if p1 and p2 are pairs of reals, pairAdd(p1,p2) is the pair (x,y), where x
# is the sum of the first coordinates of p1 and p2, and y is the sum of
# the second coordinates of p1 and p2.
def pairAdd(p1, p2):
    return (p1[0] + p2[0], p1[1] + p2[1])

# minF: list(coded cell) ~> R
# If L is a nonempty list of coded cells, then minF(L) is the member of L
# with the minimum third coordinate among the members of L,
# or the first such member, if more than one exists.
def minF(L):
    m = L[0]
    for i in range(1,len(L)):
        n = L[i]
        if n[2] < m[2]:
            m = n
    return m

# lowerF: list(coded cell) -> bool
# If L is a list of coded cells and T is a coded tile, then lowerF(L,T) if
# there exists some member of L whose first coordinate matches T's first
# coordinate and whose third coordinate is less than T's third coordinate.
def lowerF(L,T):
    for i in range(0,len(L)):
        if L[i][2] < T[2] and L[i][0] == T[0]:
            return True
    return False

# straightLineDistance: cell * cell -> R
# If A and B are cells, straightLineDistance(A,B) is the distance from the
# center of A to the center of B.
def straightLineDistance(A,B):
    x1 = A[0]
    y1 = A[1]
    x2 = B[0]
    y2 = B[1]
    temp = pow(x2-x1, 2) + pow(y2-y1, 2)
    return sqrt(temp)

# clearLineOfAttack: cell * cell * readState -> bool
# If l1 and l2 are cells, clearLineOfAttack(l1,l2) iff all cells intersected
# by the line from l1's center to l2's center, with the exception of l1 and
# l2, are unoccupied.
def clearLineOfAttack(l1, l2):
    trail = lineOfAttackSet(l1,l2).difference({l1,l2})
    return allUnoccupied(trail)

# lineOfAttackSet: cell * cell -> set(cell)
# If l1 and l2 are cells, lineOfAttackSet(l1, l2) is the set of all cells
# that would be intersected by a line segment from the center of l1 to
# the center of l2.
def lineOfAttackSet(l1,l2):
    # base case
    if l1 == l2:
        return {l1}
    # find middle cell and recur over the two halves of the line segment
    xDiff = l2[0] - l1[0]
    yDiff = l2[1] - l1[1]
    midpoint1 = (l1[0] + int(xDiff/2), l1[1] + int(yDiff/2))
    midpoint2 = (l2[0] - int(xDiff/2), l2[1] - int(yDiff/2))
    return lineOfAttackSet(l1, midpoint1) | lineOfAttackSet(midpoint2, l2)

# allUnoccupied: set(cell) * readState -> bool
# If p is a set of cells, allUnoccupied(p) iff every member of p
# is unoccupied.
def allUnoccupied(p):
    for c in p:
        if occupied(c):
                return False
    return True

# army: player -> set(int)
# army(p) is {1,2,3} if p is red, {4,5,6} if p is black, and {} otherwise.
def army(p):
    if p == "red":
        return {1,2,3}
    elif p == "black":
            return {4,5,6}
    return {}

# activeUnits: player * readState -> set(int)
# If p is a player, activeUnits(p) is the set of members of army(p) that are
# the indices of units on the board.
def activeUnits(p):
    out = set()
    for i in army(p):
        if onBoard(unitWithIndex(i)):
            out = out | {i}
    return out

# otherPlayer: player -> player
# If p is a player, otherPlayer(p) is red if p is black, and black otherwise.
def otherPlayer(p):
    if p == "black":
        return "red"
    return "black"

# currentPlayer: readState ~> player
# If ctrl is a pair and ctrl[0] is deploy, movement, or attack, then
# currentPlayer() is ctrl[1]
def currentPlayer():
    return getCtrl()[1]

# allDead: player * readState -> bool
# If p is a player, allDead(p) means no unit in p's army is on the board.
def allDead(p):
    for i in army(p):
        u = unitWithIndex(i)
        if onBoard(u):
            return False
    return True

# winner: readState -> player
# If allDead("red"), then winner() is "black". Otherwise, winner() is "red".
def winner():
    if allDead("red"):
        return "black"
    return "red"

# unitInCell: cell -> Unit U {None}
# If C is a cell, then unitInCell(C) is a unit in C, or
# None if no such unit exists.
def unitInCell(C):
    for u in getRoster():
        if unitLocation(u) == C:
            return u
    return None




















#========================
'''Game Loop Functions'''
#========================

# update: readState * readInput -> writeState
# update() executes any automatic game events that need to be executed.
# If any such events were executed, update() returns. Otherwise,
# update() gets input from the player. Then, update() goes through the
# action queue from front to back, executing every action in the queue
# whose requirements are met.
# After the above, update() clears the action queue.
def update():
    # Automatic Game Events
    if autoEvents():
        return

    # Player Input
    getInput()

    # Player Actions
    for a in getActionQueue():
        if a.reqs():
            a.effects()
    setActionQueue([])

# autoEvents() implements the automatic game events described in the
# architecture document. When one of these events is executed, autoEvents()
# immediately returns true, without checking any further events.
# If no event is executed, autoEvents() returns false.
def autoEvents():
    if getCtrl()[0] == "attack" and (allDead("red") or allDead("black")):
        setCtrl("gameOver")
        return True
    if getCtrl() == ("deploy", getFirstPlayer()):
        if allPlaced(army(getFirstPlayer())):
            setCtrl(("deploy", getSecondPlayer()))
            setActed(set())
            return True
    if getCtrl() == ("deploy", getSecondPlayer()):
        if allPlaced(army(getSecondPlayer())):
            setCtrl(("move", getFirstPlayer()))
            if getFirstPlayer() == "red":
                playBackGroundMusic(Slinger_Move_Music)
            else:
                playBackGroundMusic(Swordsman_Move_Music)
            setActed(set())
            return True
    if getCtrl()[0] == "move":
        if activeUnits(currentPlayer()) <= getActed(): # subset, in case any
                                                       # dead units in acted
            setCtrl(("attack", currentPlayer()))
            if currentPlayer() == "red":
                playBackGroundMusic(Slinger_Attack_Music)
            else:
                playBackGroundMusic(Swordsman_Attack_Music)
            setActed(set())
            return True
    if getCtrl()[0] == "attack":
        if activeUnits(currentPlayer()) <= getActed():
            setCtrl(("move", otherPlayer(currentPlayer())))
            if currentPlayer() == "red":
                playBackGroundMusic(Slinger_Move_Music)
            else:
                playBackGroundMusic(Swordsman_Move_Music)
            setActed(set())
            return True
    return False

# allPlaced: set(int) * readState -> bool
# if p is a set of integers, allPlaced(p) if every member of
# p is the index of a unit on the board.
def allPlaced(p):
    for i in p:
        u = unitWithIndex(i)
        if not onBoard(u):
            return False
    return True




















#==========
'''Input'''
#==========

# getInput: readState * readInput -> writeState
# if ctrl is "start", getInput() gets user input related to the coin toss.
# Otherwise, if ctrl is "selectFirst", getInput() gets user input related
# to selecting the first player.
# Otherwise, getInput() gets input relating to the other phases of the game.
def getInput():
    if getCtrl() == "callToss":
        getTossInput()
    elif getCtrl() == "selectFirst":
        getSelectInput()
    else:
        getMapInput()

# getTossInput: readInput -> writeState
# If Button 1 has been clicked, getTossInput() adds
# CoinToss("head") to the action queue.
# Otherwise, if Button 2 has been clicked, getTossInput()
# adds CoinToss("tail") to the action queue
def getTossInput():
    if button1():
        queueAction(CoinToss("head"))
    elif button2():
        queueAction(CoinToss("tail"))

# getSelectInput: readState * readInput -> writeState
# Let p be the coin toss winner
# If the "Choose Red" button has been clicked, getSelectInput() adds
# SelectFirstPlayer(p, "red") to the action queue.
# Otherwise, if the "Choose Black" button has been clicked, getSelectInput()
# adds SelectFirstPlayer(p, "black") to the action queue
def getSelectInput():
    if button1():
        queueAction(SelectFirstPlayer(getTossWinner(), "red"))
    elif button2():
        queueAction(SelectFirstPlayer(getTossWinner(), "black"))

# getMapInput: readState * readInput -> writeState
# If no cell has been game-clicked this frame, then getMapInput() deselects
# any currently selected unit if a game-click occurred this frame. If button 2
# was clicked this frame and the game isn't over,
# getMapInput() adds all of the current player's active units to acted.
# If a cell C has been game-clicked this frame, then getMapInput() does the
# following:
#   if the game is in the "deploy" control state, then getMapInput() attempts
#       to place the one of the current player's unplace units in C.
#   Otherwise, if no unit is selected, getMapInput() checks for unit selection
#       input.
#   Otherwise, getMapInput() checks for targetting input.
def getMapInput():
    if clickedCell() == None:
        if gameClicked():
            if button2() and getCtrl() != "gameOver":
                setActed(activeUnits(currentPlayer()))
            selectUnit(None)
    else:
        C = clickedCell()
        if getCtrl()[0] == "deploy":
            placeNextUnit(currentPlayer(),C)
        elif unitSelected() == None:
            selectUnitProcess(C)
        else:
            targetProcess(C)

# selectUnitProcess: readState -> writeState
# If C is a cell, then selectUnitProcess(C) selects the unit in cell C if such
# a unit's index is in the current player's army and not in acted.
def selectUnitProcess(C):
    clickedUnit = unitInCell(C)
    if clickedUnit == None:
        return
    i = clickedUnit.index
    if i in army(currentPlayer()) and not i in getActed():
        selectUnit(clickedUnit)
        if currentPlayer() == "red":
            playSound(Slinger_Acknowledgement)
        else:
            playSound(Swordsman_Acknowledgement)

# targetProcess: cell * readState -> writeState
# Let p be the current player and u be the currently selected unit.
# If C is a cell, then targetProcess(C) adds Move(p, u, C) to the action
# queue if the first coordinate of ctrl is "move". Otherwise, if the first
# coordinate of ctrl is "attack" and there is a unit v in cell C,
# then targetProcess(C) adds Attack(p, u, v) to the action queue.
# After the above, targetProcess(C) deselects the currently selected unit.
def targetProcess(C):
    if getCtrl()[0] == "move":
        queueAction(Move(currentPlayer(), unitSelected(), C))
    elif getCtrl()[0] == "attack":
        target = unitInCell(C)
        if target != None:
            queueAction(Attack(currentPlayer(), unitSelected(), target))
    selectUnit(None)

# placeNextUnit: player * cell * readState -> writeState
# If p is a player and C is a cell, then placeNextUnit(p,C) adds Place(p,u,C)
# to the action queue, where u is a unit such that u is not on the board and
# u's index is in army(p).
# If no such unit exists, placeNextUnit(p,C) does nothing.
def placeNextUnit(p, C):
    for i in army(p):
        u = unitWithIndex(i)
        if not onBoard(u):
            queueAction(Place(p, u, C))
            return

# gameClicked: readInput -> bool
# gameClicked() means the left mouse button was clicked this frame.
def gameClicked():
    return mouseDown and not oldMouseDown

# areaClicked: Rectangle * readInput -> bool
# If R is a rectangle, areaClicked(R) if the area represented by R
# was game-clicked this frame.
def areaClicked(R):
    return gameClicked() and R.containsPoint((mouseX, mouseY))

# button1: readInput -> bool
# button1() iff the area occupied by button 1 was game-clicked this frame.
def button1():
    return areaClicked(button1Area())

# button2: readInput -> bool
# button2() iff the area occupied by button 2 was game-clicked this frame.
def button2():
    return areaClicked(button2Area())

# clickedCell: readState -> (int * int) U {None}
# If a cell C's interior has been game-clicked this frame, clickedCell() is
# C. Otherwise, clickedCell() is None.
def clickedCell():
    root = (windowDimensions()[0]/-2.222, windowDimensions()[1]/-6.666)
    w = cellWidth()
    if gameClicked():
        for x in range(1,11):
            for y in range(1,11):
                (left, top) = pairAdd(root, (x*w, y*w))
                if areaClicked(Rectangle(left, top, w, w)):
                    return (x,y)
    return None




















#====================================
'''Init Functions & Database Layer'''
#====================================

# using global variables for the moment. Will update database layer when
# the actual database is functional

# init: readState -> writeState
# init() initializes unit statistics, the unit roster, the state variables,
# the action queue, and the interface variables.
def init():
    initStats()
    initRoster()
    initStateVars()
    initActions()
    initInterface()

# initStats: writeState
# initStats() initializes a dict stats, such that for each unit type t,
# there exists a key-value pair in stats (t:(m,r,h,a,d)), where m, r, h, a,
# and d are the respective values corresponding to the movement, range, hitRoll,
# armor, and damage of units of type t, as defined in the Maegen rules.
def initStats():
    global stats
    stats = {'slinger':(3, 3, 3, 1, 3), 'swordsman':(1, 1.5, 4, 4, 4)}

# getStats: dict
# getStats() returns stats.
def getStats():
    return stats

# initRoster: writeState
# initRoster() initializes roster as follows:
#   For each unit index i in red's army, a Slinger with index i is added to
#       roster.
#   For each unit index i in black's army, a Swordsman with index i is added to
#       roster.
def initRoster():
    global roster
    roster = set()
    for i in army("red"):
        roster = roster | { Slinger(i) }
    for i in army("black"):
        roster = roster | { Swordsman(i) }

# getRoster: readState: set(Unit)
# getRoster() returns roster.
def getRoster():
    return roster

# initLoaction: readState -> writeState
# initLocation() initializes location, setting the locations
# of all units to None.
def initLocation():
    global location
    location = dict()
    for u in getRoster():
        location[u.index] = None

# unitLocation: Unit * readState -> Cell
# If u is a unit, unitLocation(u) is the location of u (i.e. the value in
# location that has u's index as a key.)
def unitLocation(u):
    return location[u.index]

# getLocation: readState -> dict
# getLocation() returns location.
def getLocation():
    return location

# If u is a unit and C is a cell, setLocation(u,C) reassigns the key u.index to
# the value of C in location. If u.index has no value in location, the key-
# value pair (u.index:C) is added to location.
def setLocation(u,C):
    location[u.index] = C

# initStateVars: writeState
# initStateVars() declares the global state variables ctrl, tossWinner,
# firstPlayer, secondPlayer, and acted and sets them to respective values
# "callToss", None, None, None, and {}, then initializes location.
def initStateVars():
    global ctrl
    global tossWinner
    global firstPlayer
    global secondPlayer
    global acted
    ctrl = "callToss"
    tossWinner = None
    firstPlayer = None
    secondPlayer = None
    acted = {}
    initLocation()

# getCtrl: readState -> control state
# getCtrl() returns ctrl
def getCtrl():
    return ctrl

# setCtrl: control state -> writeState
# If c is a control state, setCtrl(c) sets ctrl to c.
def setCtrl(c):
    global ctrl
    ctrl = c

# getTossWinner: readState -> player U {None}
# getTossWinner() returns tossWinner.
def getTossWinner():
    return tossWinner

# setTossWinner: player -> writeState
# If p is a player, setTossWinner(p) sets tossWinner to p.
def setTossWinner(p):
    global tossWinner
    tossWinner = p

# getFirstPlayer: readState -> player U {None}
# getFirstPlayer() returns firstPlayer.
def getFirstPlayer():
    return firstPlayer

# setFirstPlayer: player -> writeState
# If p is a player, setFirstPlayer(p) sets firstPlayer to p.
def setFirstPlayer(p):
    global firstPlayer
    firstPlayer = p

# getSecondPlayer: readState -> player U {None}
# getSecondPlayer() returns secondPlayer.
def getSecondPlayer():
    return secondPlayer

# setSecondPlayer: player -> writeState
# If p is a player, setSecondPlayer(p) sets secondPlayer to p.
def setSecondPlayer(p):
    global secondPlayer
    secondPlayer = p

# getActed: readState -> set(int)
# getActed() returns acted.
def getActed():
    return acted

# setActed: set(int) -> writeState
# If a is a set of integers, setActed(a) sets acted to a.
def setActed(a):
    global acted
    acted = a

# initActions: writeState
# initActions() declares the global state variable actionQueue and
# initializes it to [].
def initActions():
    global actionQueue
    actionQueue = []

# getActiongQueue: readState -> list(PlayerAction)
# getActionQueue() returns actionQueue.
def getActionQueue():
    return actionQueue

# queueAction: PlayerAction * readState -> writeState
# queueAction(A) adds PlayerAction A to the end of actionQueue
def queueAction(A):
    global actionQueue
    actionQueue += [A]

# setActionQueue: list(PlayerAction) -> writeState
# If Q is a list of PlayerActions, setActionQueue(Q) sets actionQueue to Q.
def setActionQueue(Q):
    global actionQueue
    actionQueue = Q

# initInterface: writeState
# initInterface() initializes global variable selected to None
def initInterface():
    global selected
    selected = None

# unitSelected: readState -> player U {None}
# unitSelected() returns selected.
def unitSelected():
    return selected

# unitWithIndex: int * readState -> Unit U {None}
# If i is an integer, unitWithIndex(i) is a member of roster with i as an
# index, or None if no such member exists.
def unitWithIndex(i):
    for u in getRoster():
        if u.index == i:
            return u
    return None

# selectUnit: Unit * {None} -> writeState
# If U is a unit or None, selectUnit(U) sets selected to U.
def selectUnit(U):
    global selected
    selected = U

# movement: Unit -> R
# if U is a unit, movement(U) is U's movement field.
def movement(U):
    return U.movement

# unitRange: Unit -> R
# if U is a unit, unitRange(U) is U's unitRange field.
def unitRange(U):
    return U.unitRange

# hitRoll: Unit -> int
# if U is a unit, hitRoll(U) is U's hitRoll field.
def hitRoll(U):
    return U.hitRoll

# armor: Unit -> int
# if U is a unit, armor(U) is U's armor field.
def armor(U):
    return U.armor

# damage: Unit -> int
# if U is a unit, damage(U) is U's damage field.
def damage(U):
    return U.damage




















#====================
'''Image Functions'''
#====================

# display: readState -> list(image)
# display is a list including the following, added in the order they are
# listed:
#   The game background and the map grid
#   The sprites for all units on the board
#   The image for button 1 if ctrl is "callToss" or "selectFirst".
#   The image for button 2 if ctrl is not a pair with first coordinate "deploy".
#   The game's status message.
#   No other elements.
def display():
    base = background() + mapGrid() + allUnitImages()
    if getCtrl() in {"callToss", "selectFirst"}:
        base += button1Image()
    if getCtrl()[0] != "deploy":
        base += button2Image()
    base += statusMessage()
    return base

# background: List(image)
# background() is a list of images depicting a filled rectangle of color
# bgColor(), spanning the entirety of the window.
def background():
    d = windowDimensions()
    return frect(Rectangle(-d[0]/2, d[1]/2, d[0], d[1]), bgColor())

# statusMessage: List(image)
# statusMessage() is a list whose only member is a black, 35-pt text image,
# centered at (0,-300), such that the following is true:
#   If the game is over, the message reads "Game Over - [p] Wins", where [p]
#       is the player who won.
#   If ctrl is "callToss", the message reads "Red, Call the Coin Toss"
#   If ctrl is "selectFirst", the message reads "[p] Wins the Toss - [p], Choose
#       who Goes First", where [p] is the tossWinner
#   If ctrl is a pair whose first coordinate is "deploy", the message reads
#       "[p], Place Your Units", where [p] is the current player
#   If ctrl is a pair whose first coordinate is "move", the message reads
#       "[p], Move Your Units", where [p] is the current player
#   If ctrl is a pair whose first coordinate is "attack", the message reads
#       "[p], Attack with Your Units", where [p] is the current player
def statusMessage():
    if getCtrl() == "gameOver":
        msg = "Game Over - " + str(winner().capitalize()) + " Wins"
    elif getCtrl() == "callToss":
        msg = "Red, Call the Coin Toss"
    elif getCtrl() == "selectFirst":
        p = getTossWinner().capitalize()
        msg = p + " Wins the Toss - " + p + ", Choose who Goes First"
    else:
        p = currentPlayer().capitalize()
        if getCtrl()[0] == "deploy":
            msg = p + ", Place Your Units"
        elif getCtrl()[0] == "move":
            msg = p + ", Move Your Units"
        else:
            msg = p + ", Attack with Your Units"
    return [txt(msg, (0,windowDimensions()[1]/-2.222), int(windowDimensions()[0]/22.857), blackColor())]

# frect: Rectangle * color -> list(image)
# If R is a Rectangle and C is a color, then frect(R,C)
# is a list of two filled triangles of color C, the first of which
# has its corners at the top left, top right, and bottom left corners of R,
# and the second of which has its corners at the top right, bottom right, and
# bottom left corners of R.
def frect(R,C):
    tl = (R.left, R.top)
    bl = (R.left, R.top - R.height)
    tr = (R.left + R.width, R.top)
    br = (R.left + R.width, R.top - R.height)
    tri1 = ftri(tl, tr, bl, C)
    tri2 = ftri(tr, br, bl, C)
    return [tri1, tri2]

# mapGrid: list(image)
# mapGrid() is a list of images depicting gridColor() colored line segments
# running along the outer edges of each cell.
def mapGrid():
    out = []
    for i in range(0,mapDimensions()[1]):
        out += mapHorizSeg(i)
    for i in range(0,mapDimensions()[0]):
        out += mapVertSeg(i)
    return out

# mapHorizSeg: int -> list(image)
# if i is an integer in {0..9}, then mapHorizSeg(i) is a list of images
# depicting gridColor() colored lines running along the upper and lower edges
# of all cells of the form (x, 10-i), where x is an integer in {1..10}.
def mapHorizSeg(i):
    columns = mapDimensions()[0]
    rows = mapDimensions()[1]
    w = cellWidth()
    left = -columns/2 * w
    right = columns/2 * w
    top = rows/2 * w + verticalOffset()
    p1 = (left, top - w * i)
    p2 = (right, top - w * i)
    p3 = pairAdd(p1, (0, 1 - w))
    p4 = pairAdd(p2, (0, 1 - w))
    return [seg(p1, p2, gridColor()), seg(p3, p4, gridColor())]

# mapVertSeg: int -> list(image)
# if i is an integer in {0..9}, then mapVertSeg(i) is a list of images
# depicting gridColor() colored lines running along the left and right edges
# of all cells of the form (i+1, y), where y is an integer in {1..10}.
def mapVertSeg(i):
    columns = mapDimensions()[0]
    rows = mapDimensions()[1]
    w = cellWidth()
    left = -columns/2 * w
    top = rows/2 * w + verticalOffset()
    bottom = -rows/2 * w + verticalOffset()
    p1 = (left + w * i, top)
    p2 = (left + w * i, bottom)
    p3 = pairAdd(p1, (w - 1, 0))
    p4 = pairAdd(p2, (w - 1, 0))
    return [seg(p1, p2, gridColor()), seg(p3, p4, gridColor())]

# allUnitImages: readState -> list(image)
# allUnitImages() is a list of images depicting the sprites for all units
# on the board.
def allUnitImages():
    out = []
    for u in getRoster():
        out += unitImage(u)
    return out

# unitImage: Unit * readState -> list(image)
# If u is a unit, then if u is on the board, unitImage(u) a list depicting
# a slinger sprite in u's cell if u is a slinger, and a swordsman sprite in
# u's cell otherwise.
# If u is not on the board, unitImage(u) is an empty list.
def unitImage(u):
    Cell = unitLocation(u)
    w = cellWidth()
    if Cell == None:
        return []
    if u.index in army("red"):
        return slingerImage(u)
    else:
        return swordsmanImage(u)

# swordsmanImage(u): Unit ~> list(image)
# If u is a unit on the board, swordsmanImage(u) is a list of images
# depicting an "X" in u's cell, such that the following is true:
#   If u's index is in acted, then the "X" is of color fadedBlack()
#   Otherwise, if u is the selected unit, then the "X" is of color green()
#   Otherwise, the "X" is of color blackColor()
def swordsmanImage(u):
    Cell = unitLocation(u)
    p = topLeft(Cell)
    return [fileImg(Swordsman_Img, p)]
    # return xImage(Cell, color)

# xImage: cell * color -> list(image)
# If Cell is a cell and color is a color, xImage(Cell, color) is a list of
# two color-colored segments forming a cellWidth() * cellWidth() "X"
# centered in Cell.
def xImage(Cell, color):
    p = bottomLeft(Cell)
    left = p[0]
    right = p[0] + cellWidth()
    top = p[1] + cellWidth()
    bottom = p[1]
    s1 = seg((left, bottom), (right, top), color)
    s2 = seg((left, top), (right, bottom), color)
    return [s1, s2]

# slingerImage(u): Unit ~> list(image)
# If u is a unit on the board, then slingerImage(u) is a list whose only
# member is a circ image, centered in u's cell with a radius equal to half
# the cell width, such that the following are true:
#   If u's index is in acted, then the circ is of color fadedRed()
#   Otherwise, if u is the selected unit, then the circ is of color green()
#   Otherwise, the circ is of color redColor()
def slingerImage(u):
    Cell = unitLocation(u)
    p = topLeft(Cell)
    return [fileImg(Slinger_Img, p)]
    # return [circ(cellCenter(Cell), int(cellWidth()/2), color)]

# bottomLeft: cell -> point
# If c is a cell, bottomLeft(c) is the bottom-left corner of c.
def bottomLeft(c):
    w = cellWidth()
    x =  w * -mapDimensions()[0]/2
    y = verticalOffset() - w * mapDimensions()[1]/2
    x += (c[0] - 1) * w
    y += (c[1] - 1) * w
    return (int(x),int(y))

# topLeft: cell -> point
# If c is a cell, topLeft(c) is the top-left corner of c.
def topLeft(c):
    w = cellWidth()
    x =  w * -mapDimensions()[0]/2
    y = verticalOffset() - w * mapDimensions()[1]/2
    x += (c[0] - 1) * w
    y += (c[1]) * w
    return (int(x),int(y))

# cellCenter: cell -> point
# If c is a cell, cellCenter(c) is the point w cells to the right of and
# w cells above c's bottom-left corner, where w is half the cell width.
def cellCenter(c):
    w = cellWidth()/2
    return pairAdd(bottomLeft(c), (w,w))

# button1Image: readState -> list(image)
# button1Image() is a list of images depicting a filled rectangle over
# the rectangle represented by button1Area(), overlapped by a 25-pt
# txt image centered in the filled rectangle, such that
# the following are true:
#   If ctrl is "callToss", the filled rectangle is of color buttonColor(),
#       and the txt image is of color textColor() and reads "Heads".
#   Otherwise, the filled rectangle is of color redColor(),
#       and the txt image is of color blackColor() and reads "Red".
def button1Image():
    if getCtrl() == "callToss":
        color = buttonColor()
        message = txt("Heads", (windowDimensions()[0]/-4,windowDimensions()[1]/-3.077), int(windowDimensions()[0]/32), textColor())
    else:
        color = redColor()
        message = txt("Red", (windowDimensions()[0]/-4,windowDimensions()[1]/-3.077), int(windowDimensions()[0]/32), blackColor())
    return frect(button1Area(), color) + [message]

# button2Image: readState -> list(image)
# button2Image() is a list of images depicting a filled rectangle over
# the rectangle represented by button2Area(), overlapped by a 25-pt
# txt image centered in the filled rectangle, such that
# the following are true:
#   If ctrl is "selectFirst", the filled rectangle is of color blackColor(),
#       and the txt image is of color redColor() and reads "Black".
#   Otherwise, the filled rectangle is of color buttonColor()
#       and the txt image is of color textColor(). If ctrl is "callToss", the
#       message reads "Tails". Otherwise, it reads "Pass".
def button2Image():
    if getCtrl() == "selectFirst":
        color = blackColor()
        message = txt("Black", (windowDimensions()[0]/4,windowDimensions()[1]/-3.077), int(windowDimensions()[0]/32), redColor())
    else:
        color = buttonColor()
        if getCtrl() == "callToss":
            message = txt("Tails", (windowDimensions()[0]/4,windowDimensions()[1]/-3.077), int(windowDimensions()[0]/32), textColor())
        else:
            message = txt("Pass", (windowDimensions()[0]/4,windowDimensions()[1]/-3.077), int(windowDimensions()[0]/32), textColor())
    return frect(button2Area(), color) + [message]




















#===========
'''Colors'''
#===========

# bgColor: color
# bgColor() is (230,230,230).
def bgColor():
    return (230,230,230)

# gridColor: color
# gridColor() is (200,200,200).
def gridColor():
    return (200,200,200)

# blackColor: color
# blackColor() is (0,0,0).
def blackColor():
    return (0,0,0)

# redColor: color
# redColor() is (200,0,0).
def redColor():
    return (200,0,0)

# green: color
# green() is (0,200,0).
def green():
    return (0,200,0)

# fadedBlack: color
# fadedBlack() is (175,175,175).
def fadedBlack():
    return (175,175,175)

# fadedRed: color
# fadedRed() is (215,185,185).
def fadedRed():
    return (215,185,185)

# buttonColor: color
# buttonColor() is (100,100,220).
def buttonColor():
    return (100, 100, 220)

# textColor: color
# textColor() is blackColor().
def textColor():
    return blackColor()




















#=============
'''Database'''
#=============

#
def connectDB():
    conn = sqlite3.connect(':memory:')



















#===========
'''Sounds'''
#===========

Slinger_Acknowledgement = loadSoundFile("Slinger_Select.wav")
Slinger_Move = loadSoundFile("Slinger_Move.wav")
Slinger_Attack = loadSoundFile("Slinger_Attack.wav")
Slinger_Die = loadSoundFile("Slinger_Die.wav")
Slinger_Move_Music = "Slinger_Move_Music.wav"
Slinger_Attack_Music = "Slinger_Attack_Music.wav"
Swordsman_Acknowledgement = loadSoundFile("Swordsman_Select.wav")
Swordsman_Move = loadSoundFile("Swordsman_Move.wav")
Swordsman_Attack = loadSoundFile("Swordsman_Attack.wav")
Swordsman_Die = loadSoundFile("Swordsman_Die.wav")
Swordsman_Move_Music = "Swordsman_Music.wav"
Swordsman_Attack_Music = "Swordsman_Music.wav"




















#===========
'''Images'''
#===========
Slinger_Img = loadImageFile("Slinger.png")
Slinger_Img = scale(Slinger_Img, (int(cellWidth()), int(cellWidth())))
Swordsman_Img = loadImageFile("Swordsman.png")
Swordsman_Img = scale(Swordsman_Img, (int(cellWidth()), int(cellWidth())))
