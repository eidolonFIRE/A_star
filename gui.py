import pygame


class Button:
	def __init__(self, rect, color, text, handler, layers):
		self.rect = rect
		self.absRect = pygame.Rect(*rect)
		self.color = color
		self.text = text
		self.handler = handler
		self.layers = layers
		self.size = 0
	def draw(self, display):
		self.size = self.absRect[3]
		pygame.draw.rect(display, self.color, self.absRect)
		font = pygame.font.Font(None, self.size)
		text = font.render(self.text, 1, (0,0,0) if self.color[0] > 100 else (255,255,255))
		textpos = (
			-text.get_rect().center[0] + self.absRect[0] + self.absRect[2] * 5/10, 
			-text.get_rect().center[1] + self.absRect[1] + self.absRect[3] * 5/10)
		display.blit(text, textpos)
	def down(self, pos):
		if self.handler != None:
			self.handler()

#==============================================================================

class List:
	def __init__(self, rect, color, text, handler, layers):
		self.rect = rect
		self.absRect = pygame.Rect(*rect)
		self.color = color
		self.text = text
		self.size = 10
		self.handler = handler
		self.layers = layers
	def draw(self, display):
		self.size = min(self.absRect[3] / (len(self.text) + 1), int(self.absRect[2] / self.rect[2] / 13))
		pygame.draw.rect(display, (20,20,20), self.absRect)
		drawy = self.size
		font = pygame.font.SysFont("monospace", self.size, bold = True)
		for line in self.text:
			text = None
			if isinstance(line, list):    # support individual line color
				text = font.render(line[0], 1, line[1])
			else:
				text = font.render(line, 1, self.color)
			textpos = (self.absRect[0], - text.get_rect().center[1] + self.absRect[1] + drawy)
			display.blit(text, textpos)
			drawy = drawy + self.size
			if drawy >= self.absRect[3] - self.size / 2:
				break
	def down(self, pos):
		if self.handler != None:
			index = (int(pos[1] - self.absRect[1] - self.size / 2) / self.size)
			if index < len(self.text) and index >= 0:
				self.handler(index, pos[0] - self.absRect[0] - self.absRect[2]/2, self.text[index])

#==============================================================================

class ValueBox:
	def __init__(self, rect, color, limit, value, handler, layers):
		self.rect = rect
		self.absRect = pygame.Rect(*rect)
		self.color = color
		self.limit = limit
		self.size = 0
		self.handler = handler
		self.layers = layers
		self.value = value
	def draw(self, display):
		self.size = self.absRect[3]
		pygame.draw.rect(display, self.color, self.absRect)
		pygame.draw.polygon(display, (0,0,0),
			[(self.absRect[0] + self.absRect[2] / 20    , self.absRect[1] + self.absRect[3] / 2          ),
			 (self.absRect[0] + self.absRect[2] / 5     , self.absRect[1] + self.absRect[3] / 10         ),
			 (self.absRect[0] + self.absRect[2] / 5     , self.absRect[1] + self.absRect[3] * 9 / 10)])
		pygame.draw.polygon(display, (0,0,0),
			[(self.absRect[0] + self.absRect[2] * 19 / 20  , self.absRect[1] + self.absRect[3] / 2          ),
			 (self.absRect[0] + self.absRect[2] * 4 / 5    , self.absRect[1] + self.absRect[3] / 10         ),
			 (self.absRect[0] + self.absRect[2] * 4 / 5    , self.absRect[1] + self.absRect[3] * 9 / 10)])
		font = pygame.font.Font(None, self.size)
		text = font.render(str(self.value), 1, (0,0,0))
		textpos = (
			-text.get_rect().center[0] + self.absRect[0] + self.absRect[2] * 5/10, 
			-text.get_rect().center[1] + self.absRect[1] + self.absRect[3] * 5/10)
		display.blit(text, textpos)

	def forceLimit(self):
		if self.value > self.limit[1]:
			self.value = self.limit[1]
		if self.value < self.limit[0]:
			self.value = self.limit[0]
	def down(self, pos):
		if self.handler != None:
			if pos[0] < self.absRect[0] + self.absRect[2] / 2:
				self.value = self.value - 1
				self.forceLimit()
			else:
				self.value = self.value + 1
				self.forceLimit()
			self.handler(self.value)

#==============================================================================

class CheckBox:
	def __init__(self, rect, color, text, isChecked, handler, layers):
		self.rect = rect
		self.absRect = pygame.Rect(*rect)
		self.absRect = rect
		self.color = color
		self.text = text
		self.size = 0
		self.handler = handler
		self.layers = layers
		self.checked = isChecked
	def draw(self, display):
		self.size = self.absRect[3]
		pygame.draw.rect(display, self.color, self.absRect)
		pygame.draw.rect(display, (0,0,0),
			[self.absRect[0] + self.absRect[2] / 10, self.absRect[1] + self.absRect[3] / 10,
			 self.absRect[3] * 8/10, self.absRect[3] * 8/10])
		if self.checked:
			pygame.draw.rect(display, (255,255,255),
				[self.absRect[0] + self.absRect[2] / 10 + self.absRect[3] * 1/10, self.absRect[1] + self.absRect[3] * 2/10,
				 self.absRect[3] * 6/10, self.absRect[3] * 6/10])
		font = pygame.font.Font(None, self.size)
		text = font.render(self.text, 1, (0,0,0))
		textpos = (
			-text.get_rect().center[0] + self.absRect[0] + self.absRect[2] * 6/10, 
			-text.get_rect().center[1] + self.absRect[1] + self.absRect[3] * 5/10)
		display.blit(text, textpos)
	def down(self, pos):
		if self.handler != None:
			if self.checked:
				self.checked = False
			else:
				self.checked = True
			self.handler(self.checked)


#==============================================================================

class GUI:
	def __init__(self, display, rect):
		self.absRect = rect
		self.objects = {}
		self.mode = ""
		self.display = display
		self.sprites = {}
	def rectTrans(self, parent, child):
		return pygame.Rect(parent[0] + child[0] * parent[2], parent[1] + child[1] * parent[3], child[2] * parent[2], child[3] * parent[3])
	def resize(self, rect):
		self.absRect = rect
		for key in self.objects:
			self.objects[key].absRect = self.rectTrans(self.absRect, self.objects[key].rect)
	def draw(self):
		pygame.draw.rect(self.display, (20,20,20), self.absRect)
		for key in self.objects.keys():
			if self.mode in self.objects[key].layers or "all" in self.objects[key].layers:
				self.objects[key].draw(self.display)
	def mouseDown(self, pos):
		for key in self.objects.keys():
			if self.mode in self.objects[key].layers or "all" in self.objects[key].layers:
				if self.objects[key].absRect.collidepoint(pos):
					self.objects[key].down(pos)