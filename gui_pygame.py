import pygame

import a_star

from time import time, sleep



def resize(size = (1000, 1000)):
	myDisplay = pygame.display.set_mode((size[0],size[1]) , pygame.RESIZABLE)


def reStartSearch(point = None):
	global mySearch, myBoard
	global start, goal
	global pathData
	if point:
		if point not in mySearch.cost_so_far:
			return
	mySearch = a_star.A_Star(start, goal, myBoard)
	pathData = mySearch.reconstruct_path()

def okToAddWall(point):
	global myBoard, width, height
	x, y = point
	return (x,y) not in myBoard.walls \
		and x >= 0 and x < width \
		and y >= 0 and y < height \
		and (x,y) != start \
		and (x,y) != goal


#==============================================================================
#    Init
#
#------------------------------------------------------------------------------


pygame.init()
myDisplay = pygame.display.set_mode((1000,1000), pygame.RESIZABLE)
pygame.display.set_caption('A*')
simExit = False



#==============================================================================
#    Main loop
#
#------------------------------------------------------------------------------

width = 15
height = 15
scale = 50

resize((width*scale, height*scale))



myBoard = a_star.Board(width,height)

start = (2,2)
goal = (12,12)
# pathData = []

mySearch = a_star.A_Star(start, goal, myBoard)
mySearch.compute()
pathData = mySearch.reconstruct_path()

mouseMode = 0
frame = 0

while not simExit:
	# event = pygame.event.wait()
	# frame += 1

	time_start = time()

	if frame % 3 == 0:
		mySearch.compute(step=True)
		pathData = mySearch.reconstruct_path()
		frame += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			simExit = True
		elif event.type == pygame.KEYDOWN:
			frame = 0
			if event.key == pygame.K_q:
				simExit = True
		elif event.type == pygame.MOUSEBUTTONDOWN:
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
		pygame.draw.lines(myDisplay, (40,40,200), False, map(lambda (x,y): (x*scale+25,y*scale+25), pathData), 10)

	pygame.draw.circle(myDisplay, (10,180,10), (start[0] * scale + 25, start[1] * scale + 25), 25)
	pygame.draw.circle(myDisplay, (180,10,10), (goal[0] * scale + 25, goal[1] * scale + 25), 25)

	mySearch.draw_pygame(myDisplay)

	pygame.display.update()

	time_stop = time()

	sleep(max(min(1.0/60 - (time_stop-time_start), 1), 1.0/60))



pygame.quit()
quit()