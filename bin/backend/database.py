import mysql.connector, sqlite3, os
from mysql.connector import Error
from backend.gui_logging import Logging

logger = Logging()

class EnvironmentVariables:
    def check(*args):
        for arg in args:
            if not os.environ.get(arg):
                logger.log(f"Missing environment variable: {arg}", "ERROR")
                return False

class MySQLDatabase:
    def connect(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                logger.log("Successfully connected to the database", "SUCCESS")
        except Error as e:
            logger.log(f"{e}", "ERROR")
            self.connection = None

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            logger.log("Database connection closed", "INFO")
            logger.log("Database connection closed", "INFO")

    def execute_query(self, query, params=None):
        if self.connection is None or not self.connection.is_connected():
            logger.log("Not connected to the database", "ERROR")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            logger.log("Query executed successfully", "INFO")
            logger.log("Query executed successfully", "INFO")
        except Error as e:
            logger.log(f"{e}", "ERROR")
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
            logger.log(f"{e}", "ERROR")
        else:
            logger.log(f"{command}", "SUCCESS")

    def initialSetup(host, database, user, password):
        MySQLDatabase.connect(self=MySQLDatabase, host=host, database=database, user=user, password=password)
        MySQLDatabase.execute(self=MySQLDatabase, command="CREATE TABLE IF NOT EXISTS settings (name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL, PRIMARY KEY (name));")
        MySQLDatabase.execute(self=MySQLDatabase, command="CREATE TABLE IF NOT EXISTS router_transfer_speed (time TIME NOT NULL, upload FLOAT NOT NULL, download FLOAT NOT NULL, PRIMARY KEY (time));")
        MySQLDatabase.disconnect(self=MySQLDatabase)

class SQLiteDatabase:
    def connect(self, database: str):
        self.database = database
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.database)
            logger.log("Successfully connected to the SQLite database", "SUCCESS")
        except sqlite3.Error as e:
            logger.log(f"{e}", "ERROR")
            self.connection = None

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            logger.log("SQLite database connection closed", "INFO")

    def execute_query(self, query, params=None):
        if self.connection is None:
            logger.log("Not connected to the SQLite database", "ERROR")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            logger.log(f"Query '{query}' executed successfully", "SUCCESS")
        except sqlite3.Error as e:
            logger.log(f"{e}", "ERROR")
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
        except sqlite3.Error as e:
            logger.log(f"{e}", "ERROR")
        else:
            logger.log(f"{command}", "SUCCESS")

    def initialSetup(self, database):
        SQLiteDatabase.connect(SQLiteDatabase, database)
        SQLiteDatabase.execute(SQLiteDatabase, command="CREATE TABLE IF NOT EXISTS settings (name TEXT NOT NULL, value TEXT, PRIMARY KEY (name));")
        SQLiteDatabase.execute(SQLiteDatabase, command="INSERT INTO settings (name, value) VALUES ('fritzbox_address', '');")
        SQLiteDatabase.execute(SQLiteDatabase, command="INSERT INTO settings (name, value) VALUES ('fritzbox_user', '');")
        SQLiteDatabase.execute(SQLiteDatabase, command="INSERT INTO settings (name, value) VALUES ('fritzbox_password', '');")
        SQLiteDatabase.execute(SQLiteDatabase, command="INSERT INTO settings (name, value) VALUES ('dns_check_domain', 'google.com');")
        SQLiteDatabase.execute(SQLiteDatabase, command="INSERT INTO settings (name, value) VALUES ('refresh_interval', '');")
        SQLiteDatabase.disconnect(SQLiteDatabase)