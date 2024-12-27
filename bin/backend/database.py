import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
    def connect(self, host, database, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query, params=None):
        if self.connection is None or not self.connection.is_connected():
            print("Not connected to the database")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"Error: {e}")
            return None
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return None

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def execute(self, command):
        try:
            cursor = self.connection.cursor()
            cursor.execute(command)
            self.connection.commit()
        except Exception as e:
            print(f"Error: {e}")
        else:
            print(f"SUCCESS: {command}")

    def initialSetup(host, database, user, password):
        MySQLDatabase.connect(self=MySQLDatabase, host=host, database=database, user=user, password=password)
        MySQLDatabase.execute(self=MySQLDatabase, command="CREATE TABLE IF NOT EXISTS settings (name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL, PRIMARY KEY (name));")
        MySQLDatabase.execute(self=MySQLDatabase, command="CREATE TABLE IF NOT EXISTS router_transfer_speed (time TIME NOT NULL, upload FLOAT NOT NULL, download FLOAT NOT NULL, PRIMARY KEY (time));")
        MySQLDatabase.disconnect(self=MySQLDatabase)