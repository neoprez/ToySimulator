class Node(object):
	def __init__(self, val):
		self.val = val
		self.next = None
		self.previous = None
	
	def get_val(self):
		return self.val

	def get_next(self):
		return self.next

	def get_previous(self):
		return self.previous

	def set_val(self, val):
		self.val = val

	def set_next(self, node):
		self.next = node

class LinkedList(object):

	def __init__(self):
		self.root = None

	def insert(self, val):
		if self.root == None:
			self.root = Node(val)
		else:
			current = self.root

			while current.next is not  None:
				current = current.next

			current.next = Node(val)

	def __str__(self):
		s = ""
		
		current = self.root
		
		while current is not None:
			s += str(current.val) + " "
			current = current.next

		return s

