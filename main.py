import pygame
from time import time, sleep
import random

import a_star
import gui


#==============================================================================
#    Helper Funcs
#
#------------------------------------------------------------------------------
def resize(size):
	global myDisplay
	myDisplay = pygame.display.set_mode((size[0],size[1]) , pygame.RESIZABLE)


def reStartSearch(point = None):
	global mySearch, myBoard
	global start, goal
	global pathData
	global heurs, heurMode
	global searches
	global myGui
	if point:
		if point not in mySearch.cost_so_far:
			return
	mySearch = a_star.A_Star(start, goal, myBoard, heurs[heurMode])
	pathData = mySearch.reconstruct_path()

	for key in heurs.keys():
		searches[key] = a_star.A_Star(start, goal, myBoard, heurs[key])
		searches[key].compute()

		for idx in range(len(myGui.objects["heurs"].text)):
			if key in myGui.objects["heurs"].text[idx]:
				myGui.objects["heurs"].text[idx] = "{:1}{:15} cpu: {:4d}   len: {:3.1f}".format(">" if key == heurMode else "", key, searches[key].procTime, searches[key].cost_so_far[searches[key].current])



def okToAddWall(point):
	global myBoard, width, height
	x, y = point
	return (x,y) not in myBoard.walls \
		and x >= 0 and x < width \
		and y >= 0 and y < height \
		and (x,y) != start \
		and (x,y) != goal


def selectHeurs(index = 0, x = 0, text = ""):
	global heurMode
	textTrim = text[1:15].strip()
	print("Selected Heuristic: %s"%textTrim)
	heurMode = textTrim
	reStartSearch()


def exportWalls():
	global myBoard
	print myBoard.walls

def clrWalls():
	global myBoard
	myBoard.walls = []
	reStartSearch()

def addRandWalls():
	global myBoard, goal, start
	for x in range(myBoard.width * myBoard.height / 10):
		(x, y) = random.randint(0,myBoard.width), random.randint(0,myBoard.height)
		if (x, y) not in myBoard.walls and (x,y) != goal and (x,y) != start:
			myBoard.walls.append((x,y))
	reStartSearch()


def toggleDiagonals(x):
	global myBoard
	myBoard.diagonal = x
	reStartSearch()

def maze():
	global myBoard, goal, start
	myBoard.maze(goal, start)
	reStartSearch()

def setSpeed(x):
	global speed
	speed = x

#==============================================================================
#    Heuristics
#
#------------------------------------------------------------------------------
def heuristic_basic(self, a, b):
	(x1, y1) = a
	(x2, y2) = b
	return (abs(x2 - x1) + abs(y2 - y1))

def heuristic_weighted(self, a, b):
	(x1, y1) = a
	(x2, y2) = b
	return (abs(x2 - x1) + abs(y2 - y1)) * 1.4

def heuristic_directional(self, a, b):
	(x1, y1) = a
	(x2, y2) = b
	delta = self._delta(self._sub(self.current,a), self._sub(self.current,self.goal)) + 1
	return (abs(x2 - x1) + abs(y2 - y1)) * delta

def heuristic_dist(self, a, b):
	return self._cost(a,b)

def heuristic_hybrid(self, a, b):
	(x1, y1) = a
	(x2, y2) = b
	delta = self._delta(self._sub(self.current,a), self._sub(self.current,self.goal)) + 1
	return (abs(x2 - x1) + abs(y2 - y1)) * 1.4 * delta


heurs = {
	"basic": heuristic_basic,
	"weighted": heuristic_weighted,
	"directional": heuristic_directional,
	"distance": heuristic_dist,
	"hybrid": heuristic_hybrid,
}

#==============================================================================
#    Init
#
#------------------------------------------------------------------------------


simExit = False

width = 50
height = 25
scale = 30

speed = 0
gif = False

heurMode = "basic"


pygame.init()
myDisplay = pygame.display.set_mode((width*scale,height*scale+200), pygame.RESIZABLE)
pygame.display.set_caption('A*')


# setup GUI
myGui = gui.GUI(myDisplay, (10, height*scale + 10, width * scale - 20, 180))

myGui.objects["heurs"]            = gui.List(     (0.4, 0.1,  0.5,  0.8), (250,250,250), heurs.keys(), selectHeurs, ["all"])
myGui.objects["exportWalls"]      = gui.Button(   (0.0, 0.0,  0.2, 0.18), (150,150,150), "Export Walls", exportWalls, ["all"])
myGui.objects["clrWalls"]         = gui.Button(   (0.0, 0.2,  0.2, 0.18), (150,150,150), "Clear Walls", clrWalls, ["all"])
myGui.objects["addRandWalls"]     = gui.Button(   (0.0, 0.4,  0.2, 0.18), (150,150,150), "Add Rand Walls", addRandWalls, ["all"])
myGui.objects["Maze"]             = gui.Button(   (0.0, 0.6,  0.2, 0.18), (150,150,150), "Make Maze", maze, ["all"])
myGui.objects["diagonal"]         = gui.CheckBox( (0.0, 0.8,  0.2, 0.18), (150,150,150), "Diagonal Moves", True, toggleDiagonals, ["all"])

myGui.objects["speedLabel"]       = gui.Button(   (0.22, 0.0, 0.1,  0.2), (20,20,20), "Delay", None, ["all"])
myGui.objects["speed"]            = gui.ValueBox( (0.22, 0.2, 0.1, 0.18), (150,150,150), (0,10), 0, setSpeed, ["all"])

myGui.resize((10, height*scale + 10, width * scale - 20, 180))

#==============================================================================
#    Main loop
#
#------------------------------------------------------------------------------



myBoard = a_star.Board(width,height, scale)

start = (int(width * 0.1),int(height * 0.1))
goal  = (int(width * 0.9),int(height * 0.9))

mySearch = a_star.A_Star(start, goal, myBoard, heurs["basic"])
mySearch.compute()

searches = {}

pathData = mySearch.reconstruct_path()



mouseMode = 0
frame = 0

while not simExit:
	time_start = time()

	if speed > 0:
		frame += 1

	if frame % (speed+1) == 0:
		mySearch.compute(step=speed > 0)
		pathData = mySearch.reconstruct_path()
		frame += 1
		if gif:
			pygame.image.save(myDisplay, "screens/screen_%d.png"%frame)
		

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			simExit = True
		elif event.type == pygame.KEYDOWN:
			frame += 1
			if event.key == pygame.K_q:
				simExit = True
		elif event.type == pygame.MOUSEBUTTONDOWN:
			myGui.mouseDown(pygame.mouse.get_pos())
			x, y = pygame.mouse.get_pos()
			x = x / scale
			y = y / scale
			if (x,y) in myBoard.walls:
				myBoard.walls.remove((x,y))
				mouseMode = -1
				reStartSearch()
			else:
				if okToAddWall((x,y)):
					myBoard.walls.append((x,y))
					mouseMode = 1
					reStartSearch((x,y))

		elif event.type == pygame.MOUSEMOTION:
			x, y = pygame.mouse.get_pos()
			x = x / scale
			y = y / scale

			if mouseMode == 1:
				if okToAddWall((x,y)):
					myBoard.walls.append((x,y))
					reStartSearch((x,y))
			elif mouseMode == -1:
				if (x,y) in myBoard.walls:
					myBoard.walls.remove((x,y))
					reStartSearch()

		elif event.type == pygame.MOUSEBUTTONUP:
			mouseMode = 0


		elif event.type == pygame.VIDEORESIZE:
			resize((event.w, event.h))
			continue

	
	myDisplay.fill((0,0,0))


	myBoard.draw_pygame(myDisplay)

	if len(pathData) > 1:
		pygame.draw.lines(myDisplay, (40,40,200), False, map(lambda (x,y): (x*scale+scale/2,y*scale+scale/2), pathData), 10)

	pygame.draw.circle(myDisplay, (10,180,10), (start[0] * scale + scale/2, start[1] * scale + scale/2), scale / 2)
	pygame.draw.circle(myDisplay, (180,10,10), (goal[0] * scale + scale/2, goal[1] * scale + scale/2), scale / 2)

	mySearch.draw_pygame(myDisplay)

	myGui.draw()

	pygame.display.update()

	time_stop = time()

	sleep(max(min(1.0/60 - (time_stop-time_start), 1), 1.0/1000))

pygame.quit()
quit()