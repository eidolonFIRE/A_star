import pygame
import heapq
import math



class PriorityQueue(object):
	def __init__(self):
		super(PriorityQueue, self).__init__()
		self.elements = []
		self.items = {}
	def empty(self):
		return len(self.elements) == 0
	
	def push(self, item, priority):
		if item in self.items.keys():
			p = self.items[item]
			self.elements.remove((p,item))
		self.items[item] = priority
		heapq.heappush(self.elements, (priority, item))

	
	def pop(self):
		point = heapq.heappop(self.elements)
		del self.items[point[1]]
		return point
		


class Board(object):
	def __init__(self, width, height, scale):
		super(Board, self).__init__()
		self.width = width
		self.height = height
		self.scale = scale
		self.walls = []


	def moveOptions(self, pos):
		x, y = pos
		retval = []
		# TODO: replace with map lambda
		for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
			nx, ny = (x+dx, y+dy)
			if nx >= 0 and nx < self.width and ny >= 0 and ny < self.height:
				if (nx, ny) not in self.walls:
					retval.append((nx, ny))
		return retval

	def draw_pygame(self, display):
		size = int(self.scale * 0.9)
		offset = int(self.scale * 0.1)
		for x in range(self.width):
			for y in range(self.height):
				if (x,y) in self.walls:
					pygame.draw.rect(display, (180, 180, 180), (x*self.scale+offset,y*self.scale+offset,size,size))
				else:
					pygame.draw.rect(display, (50, 50, 50), (x*self.scale+offset,y*self.scale+offset,size,size))


		

class A_Star(object):
	"""docstring for A_Star"""
	def __init__(self, start, goal, board, heuristic):
		super(A_Star, self).__init__()
		self.frontier = PriorityQueue()
		self.frontier.push(start, 0)
		self.came_from = {start: start}
		self.cost_so_far = {start: 0}
		self.start = start
		self.goal = goal
		self.board = board
		self.done = False

		# for drawing purposes
		self.current = start 
		self.highestCost = 1
		self.highestPriority = 2
		self.lowestPriority = 1
		self.heuristic = heuristic

		# timers for stats
		self.procTime = 0





	def _cost(self, a, b):
		return self._norm(self._sub(a,b))

	def _sub(self, a, b):
		return (b[0] - a[0], b[1] - a[1])

	def _dot(self, a, b):
		return a[0]*b[0] + a[1]*b[1]

	def _cross(self, a, b):
		return a[1]*b[0] - a[0]*b[1]

	def _norm(self, a):
		return math.sqrt(a[0]**2 + a[1]**2)

	def _delta(self, a, b):
		return math.acos(self._dot(a,b) / (self._norm(a) * self._norm(b)))


	def compute(self, step=False):
		while not self.frontier.empty() and not self.done:
			p, current = self.frontier.pop()
			self.lowestPriority = p # <-- for rendering purposes
			self.current = current  # <-- for rendering purposes
			if current == self.goal:
				self.done = True
				break
			
			for move in self.board.moveOptions(current):
				new_cost = self.cost_so_far[current] + self._cost(current, move)
				if move not in self.cost_so_far or new_cost < self.cost_so_far[move]:
					self.procTime += 1
					self.highestCost = max(self.highestCost, new_cost)  # <-- for rendering purposes
					self.cost_so_far[move] = new_cost
					priority = new_cost + self.heuristic(self, move, self.goal)
					self.highestPriority = max(self.highestPriority, priority)   # <-- for rendering purposes
					self.frontier.push(move, priority)
					self.came_from[move] = current
			if step:
				break
		return self.came_from, self.cost_so_far


	def reconstruct_path(self):
		if self.done:
			current = self.goal
		else:
			current = self.current
		path = []
		while current != self.start:
			path.append(current)
			current = self.came_from[current]
		path.append(self.start)
		# path.reverse()
		return path


	def draw_pygame(self, display):
		# priorities
		font = pygame.font.Font(None, self.board.scale / 2)
		for p, (x,y) in self.frontier.elements:
			pscale = (p - self.lowestPriority) / (self.highestPriority - self.lowestPriority) * 255
			pygame.draw.circle(display, (20,20,20), (x * self.board.scale + self.board.scale/2, y * self.board.scale + self.board.scale/2), self.board.scale / 2)

			color = (max(min(pscale, 255), 0), 50, max(min(255 - pscale, 255), 0))

			text = font.render("%.1f"%p, 1, color)
			textpos = (
				-text.get_rect().center[0] + x * self.board.scale + self.board.scale / 2, 
				-text.get_rect().center[1] + y * self.board.scale + self.board.scale * 3 / 4)
			display.blit(text, textpos)


		# text
		font = pygame.font.Font(None, self.board.scale * 2 / 3)
		for (x, y), cost in self.cost_so_far.items():
			if (x,y) in self.came_from:
				(a,b) = self.came_from[(x,y)]
				# pygame.draw.line(display, (40,40,200), \
				# 	(int((a+x*2.0)/3.0*self.board.scale+self.board.scale/2),int((b+y*2.0)/3.0*self.board.scale+self.board.scale/2)), \
				# 	(int((a+x)/2.0*self.board.scale+self.board.scale/2),int((b+y)/2.0*self.board.scale+self.board.scale/2)), \
				# 	4 )
				pygame.draw.line(display, (40,40,200), \
					(int(a*self.board.scale+self.board.scale/2),int(b*self.board.scale+self.board.scale/2)), \
					(int(x*self.board.scale+self.board.scale/2),int(y*self.board.scale+self.board.scale/2)), 2)


			scale = 255.0 / self.highestCost
			color = (max(min(cost*scale, 255), 0), max(min(255 - cost*scale, 255), 0), 50)

			text = font.render("%.1f"%cost, 1, color)
			textpos = (
				-text.get_rect().center[0] + x * self.board.scale + self.board.scale / 2, 
				-text.get_rect().center[1] + y * self.board.scale + self.board.scale / 3)
			display.blit(text, textpos)
