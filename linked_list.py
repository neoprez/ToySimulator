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
		self.numb_nodes = 0

	def insert_last(self, val):
		previous = None
		self.numb_nodes += 1

		if self.root == None:
			self.root = Node(val)
		else:
			current = self.root

			while current.next is not None:
				current = current.next

			newNode = Node(val)
			newNode.previous = current
			current.next = newNode

	def insert_first(self, val):
		tmpNode = self.root
		self.root = None
		newNode = Node(val)
		newNode.next = tmpNode
		self.root = newNode
		self.numb_nodes += 1

	def get_last(self):
		current = self.root

		while current.next is not None:
			current = current.next

		return current

	def get_first(self):
		return self.root

	def get_node_at(self, index):
		current = self.root

		if index == 0:
			return current
		else: 
			idx = 0
			while idx is not index and current is not None :
				current = current.next
				idx += 1

			return current

	def get_node_count(self):
		return self.numb_nodes

	def __str__(self):
		s = ""
		
		current = self.root
		
		while current is not None:
			s += str(current.val) + " "
			current = current.next

		return s

"""l = LinkedList()

for i in range(100):
	l.insert_first(i)

print l

val = l.get_value_at(50)
print val"""
