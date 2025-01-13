import json, os, re
from nicegui import ui
from backend.gui_logging import Logging
from frontend.overview import Overview
from backend.database import MySQLDatabase, SQLiteDatabase, EnvironmentVariables

logger = Logging()
sqldb = SQLiteDatabase()
mysql = MySQLDatabase()

class Settings:
    def loadVariables(self):
        if not EnvironmentVariables.check('DB_MODE','DB_HOST','DB_PORT','DB_NAME','DB_USER','DB_PASSWORD'):
            logger.log("Environment variables not complete, defaulting to standard values")
            self.db_mode = "sqlite"
            self.db_name = "database.db"
        else:
            self.db_mode = os.environ.get('DB_MODE')
            self.db_host = os.environ.get('DB_HOST')
            self.db_port = os.environ.get('DB_PORT')
            self.db_name = os.environ.get('DB_NAME')
            self.db_user = os.environ.get('DB_USER')
            self.db_pass = os.environ.get('DB_PASSWORD')

    def create(self):
        def create_settings_item(label_text, value, password_field=False):
            with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                ui.label(label_text).style('font-size: 1.25rem; font-weight: bold; width: 10em')
                input_field = ui.input(value=value, password=password_field, password_toggle_button=password_field).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
            return input_field

        with ui.column().style('padding: 1em; display: flex;'):
            with ui.grid().classes('p-0 gap-0').style('width: 100%; border-bottom: solid 8px #1577cf; border-bottom-left-radius: 8px; display: flex;'):
                ui.label('General settings').style('font-size: 2rem; font-weight: bold; color: white; padding: 0.25em; background-color: #1577cf; border-radius: 8px 8px 0px 8px; margin-bottom: -8px;')
            with ui.row().style('display: flex; flex-wrap: wrap; justify_content: left; flex-direction: row;'):
                with ui.list().style('width: 100%;'):

                    self.loadVariables()
                    if self.db_mode == 'sqlite':
                        self.database_path = str(os.path.join("config", "database.db"))
                        if not os.path.exists(self.database_path):
                            sqldb.initialSetup(self.database_path)
                        sqldb.connect(self.database_path)
                        self.address_value = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_address'")[0]
                        self.username_value = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_user'")[0]
                        self.password_value = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_password'")[0]
                        self.domain_value = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'dns_check_domain'")[0]
                        self.refresh_interval = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'refresh_interval'")[0]
                        sqldb.disconnect()

                    address = create_settings_item('FRITZ!Box Address', self.address_value)
                    username = create_settings_item('Fritz!Box User', self.username_value)
                    password = create_settings_item('Fritz!Box Password', self.password_value, True)
                    domain = create_settings_item('Check Domain', self.domain_value)

                    ui.label('Overview Refresh Interval (seconds)').style('font-size: 1.25rem; font-weight: bold;')
                    refresh_interval_slider = ui.slider(min=5, max=600, value=self.refresh_interval).style('width: 100%;')
                    refresh_interval_label = ui.label(f'{self.refresh_interval} seconds').style('font-size: 1rem;')
                    refresh_interval_slider.on_value_change(lambda: refresh_interval_label.set_text(f'{refresh_interval_slider.value} seconds'))
                    ui.button('Save').style('width: 100%; display: flex; justify_content: flex-start;').on_click(lambda: save_settings(address.value, username.value, password.value, domain.value, refresh_interval_slider.value))

        def save_settings(address: str, username: str, password: str, domain: str, refresh_interval: int):
            if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', address):
                print(address)
                ui.notify('Invalid IP address format', color='red', type='negative')
                logger.log('Invalid IP address format', 'ERROR')
                return
            elif not address:
                ui.notify('IP address cannot be empty', color='red', type='negative')
                logger.log('IP address cannot be empty', 'ERROR')
                return
            if not username:
                ui.notify('Username cannot be empty', color='red', type='negative')
                logger.log('Username cannot be empty', 'ERROR')
                return
            elif not re.match(r'^[\w\-_]+$', username):
                ui.notify('Username can only contain letters, digits, underscores, and hyphens', color='red', type='negative')
                logger.log('Username can only contain letters, digits, underscores, and hyphens', 'ERROR')
                return
            if not password:
                ui.notify('Password cannot be empty', color='red', type='negative')
                logger.log('Password cannot be empty', 'ERROR')
                return
            elif len(password) < 8:
                ui.notify('Password must be at least 8 characters long', color='red', type='negative')
                logger.log('Password must be at least 8 characters long', 'ERROR')
                return
            if not domain:
                ui.notify('Domain cannot be empty', color='red', type='negative')
                logger.log('Domain cannot be empty', 'ERROR')
                return
            elif not re.match(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$', domain):
                ui.notify('Invalid domain format', color='red', type='negative')
                logger.log('Invalid domain format', 'ERROR')
                return
            if self.db_mode == 'sqlite':
                sqldb.connect(self.database_path)
                sqldb.execute_query(f"UPDATE settings SET value = '{address}' WHERE name LIKE 'fritzbox_address';")
                sqldb.execute_query(f"UPDATE settings SET value = '{username}' WHERE name LIKE 'fritzbox_user';")
                sqldb.execute_query(f"UPDATE settings SET value = '{password}' WHERE name LIKE 'fritzbox_password';")
                sqldb.execute_query(f"UPDATE settings SET value = '{domain}' WHERE name LIKE 'fritzbox_dns_check_domain';")
                sqldb.execute_query(f"UPDATE settings SET value = '{refresh_interval}' WHERE name LIKE 'refresh_interval';")
                sqldb.disconnect()
            Overview().reload(refresh_interval)
            ui.notify('Settings saved', color='green', type='positive')
            logger.log('Settings saved', 'SUCCESS')
