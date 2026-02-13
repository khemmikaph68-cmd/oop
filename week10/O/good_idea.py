from abc import ABC, abstractmethod

class Shape:
    def area(self):
        @abstractmethod
        def area(self):
            pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def area(self):
        return 3.14159 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def area(self):
        return self.width * self.height
    
def calculate_area(shape):
    return shape.area()