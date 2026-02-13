class App:
    def __init__(self):
        self.database = MySQLDatabase()
    def save_data(self, data):
        self.database.save(data)

class MySQLDatabase:
    def save(self, data):
        print("Saving data to MySQL database...")

app = App()
app.save_data("some important data")