class BasicIterator:
    """
    Generic Iterator class for iterating over a collection of items
    """

    def __init__(self, items):
        self.items = items
        self.index = 0

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration

        ret = self.items[self.index]
        self.index += 1
        return ret
