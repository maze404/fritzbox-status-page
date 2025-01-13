import mysql.connector
from mysql.connector import Error
from backend.gui_logging import Logging

logger = Logging()

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
                logger.log("Successfully connected to the database", "INFO")
        except Error as e:
            logger.log(f"Error: {e}", "ERROR")
            self.connection = None

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            logger.log("Database connection closed", "INFO")

    def execute_query(self, query, params=None):
        if self.connection is None or not self.connection.is_connected():
            logger.log("Not connected to the database", "WARNING")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            logger.log("Query executed successfully", "INFO")
        except Error as e:
            logger.log(f"Error: {e}", "ERROR")
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
            logger.log(f"Error: {e}", "ERROR")
        else:
            logger.log(f"SUCCESS: {command}", "SUCCESS")


MySQLDatabase.connect(MySQLDatabase, host='192.168.178.33', database='fritzbox-status-page', user='fritzbox-status-page', password='dutimopt')
MySQLDatabase().execute(command="CREATE TABLE IF NOT EXISTS settings (name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL, PRIMARY KEY (name));")
MySQLDatabase().execute(command="INSERT INTO `settings`(`name`, `value`) VALUES ('fritzbox_address','192.168.178.1');")
MySQLDatabase().execute(command="INSERT INTO `settings`(`name`, `value`) VALUES ('username','api-user');")
MySQLDatabase().execute(command="INSERT INTO `settings`(`name`, `value`) VALUES ('password','51605728531983842826');")
MySQLDatabase().execute(command="INSERT INTO `settings`(`name`, `value`) VALUES ('domain','60');")
MySQLDatabase().disconnect()