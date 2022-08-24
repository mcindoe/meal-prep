class BasicIterator:
	"""
	Generic Iterator class for iterating over a collection of items
	"""

	def __init__(self, collection):
		self.collection = collection
		self.index = 0

	def __next__(self):
		if self.index >= len(self.collection):
			raise StopIteration

		ret = self.collection[self.index]
		self.index += 1
		return ret