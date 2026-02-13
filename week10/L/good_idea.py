from abc import abstractmethod
from ctypes import resize

class Shape:
    @abstractmethod
    def resize(self, new_width, new_height):
       pass
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
    
    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def resize(self, new_width, new_height):
        self.side = new_width
        self.side = new_height

    def area(self):
        return self.side * self.side
    
def resize(shape, new_width, new_height):
    shape.resize(new_width, new_height)
    return shape.area()

rect = Rectangle(2, 3)
resize(rect, 4, 5)
print("Resizing area:", rect.area())
square = Square(3)
resize(square, 4, 5)