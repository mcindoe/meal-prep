class OutOfMealsError(Exception):
    """Raised when no more meals are left to choose from"""

    def __init__(self, message: str = "Out of meals"):
        self.message = message
        super().__init__(self.message)
