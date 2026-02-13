class Machine:
    def print(self, document):
        pass
    def scan(self, document):
        pass
    def fax(self, document):
        pass

class OldFashionedPrinter(Machine):
    def print(self, document):
        print("Printing document...")
    def scan(self, document):
        raise NotImplementedError("this printer cannot scan")
    def fax(self, document):
        raise NotImplementedError("this printer cannot fax")