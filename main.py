import pygame
from time import time, sleep
import sys
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
	global heurs, heurm
	if point:
		if point not in mySearch.cost_so_far:
			return
	mySearch = a_star.A_Star(start, goal, myBoard, heurs[heurMode])
	pathData = mySearch.reconstruct_path()


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
	print("Selected Heuristic: %s"%text)
	heurMode = text
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


heurs = {
	"basic": heuristic_basic,
	"weighted": heuristic_weighted,
	"directional": heuristic_directional,
	"distance": heuristic_dist,
}

#==============================================================================
#    Init
#
#------------------------------------------------------------------------------


simExit = False

width = 40
height = 30
scale = 30

speed = 0
step = False
gif = False

heurMode = "basic"

for idx, txt in enumerate(sys.argv):
	if "-s" in txt:
		if "step" in sys.argv[idx+1]:
			step = True
			speed = 2
		else:
			speed = float(sys.argv[idx+1])**2
		

	elif "-gif" in txt:
		gif = True
		verbose = True

	elif "-dest" in txt:
		build = "dest"

	elif "-h" in txt:
		print("\
	s: frame delay when verbose (seconds)\n\
	gif: save each frame using shutter\n\
	h: print help\n")

pygame.init()
myDisplay = pygame.display.set_mode((width*scale,height*scale+200), pygame.RESIZABLE)
pygame.display.set_caption('A*')


# setup GUI
myGui = gui.GUI(myDisplay, (10, height*scale + 10, width * scale - 20, 180))

myGui.objects["heurs"]            = gui.List((   0.5,  0.1, 0.2,  0.8), (250,250,250), heurs.keys(), selectHeurs, ["all"])
myGui.objects["exportWalls"]      = gui.Button(( 0.1,  0.1, 0.2, 0.18), (150,150,150), "Export Walls", exportWalls, ["all"])
myGui.objects["clrWalls"]         = gui.Button(( 0.1,  0.3, 0.2, 0.18), (150,150,150), "Clear Walls", clrWalls, ["all"])
myGui.objects["addRandWalls"]     = gui.Button(( 0.1,  0.5, 0.2, 0.18), (150,150,150), "Add Rand Walls", addRandWalls, ["all"])

myGui.objects["Label_ProcCost"]   = gui.Button(( 0.8,  0.1, 0.2, 0.2), (150,150,150), "", None, ["all"])
myGui.objects["Label_TravelCost"] = gui.Button(( 0.8,  0.3, 0.2, 0.2), (150,150,150), "", None, ["all"])
myGui.objects["Label_Perf"]       = gui.Button(( 0.8,  0.5, 0.2, 0.2), (150,150,150), "", None, ["all"])

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
pathData = mySearch.reconstruct_path()

mouseMode = 0
frame = 0

while not simExit:
	time_start = time()

	if not step:
		frame += 1

	if speed == 0 or frame % speed == 0:
		mySearch.compute(step=speed > 0)
		pathData = mySearch.reconstruct_path()
		frame += 1
		if gif:
			pygame.image.save(myDisplay, "screens/screen_%d.png"%frame)


		myGui.objects["Label_ProcCost"].text = " Proc: %d" % mySearch.procTime
		myGui.objects["Label_TravelCost"].text = "Route: %d" % mySearch.cost_so_far[mySearch.current]
		myGui.objects["Label_Perf"].text = " Perf: %5.3f%%" % (mySearch.cost_so_far[mySearch.current] / mySearch.procTime)

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