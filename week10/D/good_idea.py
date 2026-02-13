from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self):
        pass

class MySQLDatabase(Database):
    def save(self):
        print("Saving data to MySQL database...")

class PostgreSQLDatabase(Database):
    def save(self, data):
        print(f"Saving data to PostgreSQL database...")

class App:
    def __init__(self, database: Database):
        self.database = database

    def save_data(self, data):
        self.database.save(data)

