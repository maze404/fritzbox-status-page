import json, os, re
from nicegui import ui
from backend.gui_logging import Logging
from frontend.overview import Overview
from backend.database import MySQLDatabase as database

logger = Logging()

class Settings:
    def __init__(self):
        self.settings_dir = 'config'

    def _ensure_settings_dir_exists(self):
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

    def create(self):
        self._ensure_settings_dir_exists()
        self.GeneralSettings().create()
        self.DatabaseSettings().create()

    class GeneralSettings:
        def __init__(self):
            self.settings_path = os.path.join(Settings().settings_dir, 'settings.json')

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
                        if os.path.exists(self.settings_path):
                            with open(self.settings_path, 'r') as json_file:
                                settings = json.load(json_file)
                                address_value = settings.get('address', '')
                                username_value = settings.get('username', '')
                                password_value = settings.get('password', '')
                                domain_value = settings.get('domain', '')
                                refresh_interval = settings.get('refresh_interval', '')
                        else:
                            address_value = ''
                            username_value = ''
                            password_value = ''
                            domain_value = ''
                            refresh_interval = 60

                        address = create_settings_item('FRITZ!Box Address', address_value)
                        username = create_settings_item('Fritz!Box User', username_value)
                        password = create_settings_item('Fritz!Box Password', password_value, True)
                        domain = create_settings_item('Check Domain', domain_value)
                        ui.label('Overview Refresh Interval (seconds)').style('font-size: 1.25rem; font-weight: bold;')
                        refresh_interval_slider = ui.slider(min=5, max=600, value=refresh_interval).style('width: 100%;')
                        refresh_interval_label = ui.label(f'{refresh_interval} seconds').style('font-size: 1rem;')
                        refresh_interval_slider.on_value_change(lambda: refresh_interval_label.set_text(f'{refresh_interval_slider.value} seconds'))
                        ui.button('Save').style('width: 100%; display: flex; justify_content: flex-start;').on_click(lambda: save_settings(address.value, username.value, password.value, domain.value, refresh_interval_slider.value))

            def save_settings(address: str, username: str, password: str, domain: str, refresh_interval: int):
                if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', address):
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
                if os.path.exists(Settings.DatabaseSettings().database_settings_path) and Settings.DatabaseSettings.create().use_database:
                    with open(self.database_settings_path, 'r') as json_file:
                        settings = json.load(json_file)
                        db_host = settings.get('database_host', '')
                        db_name = settings.get('database_name', '')
                        db_user = settings.get('database_user', '')
                        db_pass = settings.get('database_password', '')
                        database.connect(database, db_host, db_name, db_user, db_pass)
                        database.execute(command=f"""
                            INSERT INTO `settings`(`name`, `value`) VALUES ('address','{address}') ON DUPLICATE KEY UPDATE `value`='{address}';
                            INSERT INTO `settings`(`name`, `value`) VALUES ('username','{username}') ON DUPLICATE KEY UPDATE `value`='{username}';
                            INSERT INTO `settings`(`name`, `value`) VALUES ('password','{password}') ON DUPLICATE KEY UPDATE `value`='{password}';
                            INSERT INTO `settings`(`name`, `value`) VALUES ('domain','{domain}') ON DUPLICATE KEY UPDATE `value`='{domain}';
                        """)
                        database.disconnect()
                settings = {
                    'address': address,
                    'username': username,
                    'password': password,
                    'domain': domain,
                    'refresh_interval': refresh_interval
                }
                if os.path.exists(self.settings_path):
                    os.remove(self.settings_path)
                with open(self.settings_path, 'w') as json_file:
                    json.dump(settings, json_file, indent=4)
                Overview().reload(refresh_interval)
                ui.notify('Settings saved.', color='green', type='positive')
                logger.log('Settings saved.', 'SUCCESS')

    class DatabaseSettings:
        def __init__(self):
            self.database_settings_path = os.path.join(Settings().settings_dir, 'database.json')

        def create(self):
            with ui.grid().classes('p-0 gap-0').style('width: 100%; border-bottom: solid 8px #1577cf; border-bottom-left-radius: 8px; display: flex;'):
                ui.label('Database settings').style('font-size: 2rem; font-weight: bold; color: white; padding: 0.25em; background-color: #1577cf; border-radius: 8px 8px 0px 8px; margin-bottom: -8px;')
            with ui.row().style('display: flex; flex-wrap: wrap; justify_content: left; flex-direction: row;'):
                with ui.list().style('width: 100%;'):
                    if os.path.exists(self.database_settings_path):
                        self.use_database = ui.checkbox('Use database', value=True)
                    else:
                        self.use_database = ui.checkbox('Use database', value=False)
                    if self.use_database.value and os.path.exists(self.database_settings_path):
                        with open(self.database_settings_path, 'r') as json_file:
                            settings = json.load(json_file)
                            db_host = settings.get('database_host', '')
                            db_name = settings.get('database_name', '')
                            db_user = settings.get('database_user', '')
                            db_pass = settings.get('database_password', '')
                    else:
                            db_host = ''
                            db_name = ''
                            db_user = ''
                            db_pass = ''
                    with ui.grid(columns=1).style('width: 100%').bind_visibility_from(self.use_database, 'value'):
                        with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                            ui.label('Database Host').style('font-size: 1.25rem; font-weight: bold; width: 10em')
                            database_host = ui.input(value=db_host).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
                        with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                            ui.label('Database Name').style('font-size: 1.25rem; font-weight: bold; width: 10em')
                            database_name = ui.input(value=db_name).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
                        with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                            ui.label('Database User').style('font-size: 1.25rem; font-weight: bold; width: 10em')
                            database_user = ui.input(value=db_user).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
                        with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                            ui.label('Database Password').style('font-size: 1.25rem; font-weight: bold; width: 10em')
                            database_pass = ui.input(value=db_pass, password=True, password_toggle_button=True).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
                    ui.button('Save').style('width: 100%; display: flex; justify_content: flex-start;').on_click(lambda: save_settings(self.use_database.value, database_host.value, database_name.value, database_user.value, database_pass.value))

            def save_settings(use_database: bool, database_host: str, database_name: str, database_user: str, database_pass: str):
                if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', database_host):
                    ui.notify('Invalid IP address format', color='red', type='negative')
                    logger.log('Invalid IP address format', 'ERROR')
                    return
                elif not database_host:
                    ui.notify('IP address cannot be empty', color='red', type='negative')
                    logger.log('IP address cannot be empty', 'ERROR')
                    return
                if not database_name:
                    ui.notify('Username cannot be empty', color='red', type='negative')
                    logger.log('Username cannot be empty', 'ERROR')
                    return
                elif not re.match(r'^[\w\-_]+$', database_name):
                    ui.notify('Username can only contain letters, digits, underscores, and hyphens', color='red', type='negative')
                    logger.log('Username can only contain letters, digits, underscores, and hyphens', 'ERROR')
                    return
                if not database_user:
                    ui.notify('Username cannot be empty', color='red', type='negative')
                    logger.log('Username cannot be empty', 'ERROR')
                    return
                elif not re.match(r'^[\w\-_]+$', database_user):
                    ui.notify('Username can only contain letters, digits, underscores, and hyphens', color='red', type='negative')
                    logger.log('Username can only contain letters, digits, underscores, and hyphens', 'ERROR')
                    return
                if not database_pass:
                    ui.notify('Password cannot be empty', color='red', type='negative')
                    logger.log('Password cannot be empty', 'ERROR')
                    return
                elif len(database_pass) < 8:
                    ui.notify('Password must be at least 8 characters long', color='red', type='negative')
                    logger.log('Password must be at least 8 characters long', 'ERROR')
                    return
                settings = {
                    'use_database': use_database,
                    'database_host': database_host,
                    'database_name': database_name,
                    'database_user': database_user,
                    'database_password': database_pass
                }
                if os.path.exists(self.database_settings_path):
                    os.remove(self.database_settings_path)
                with open(self.database_settings_path, 'w') as json_file:
                    json.dump(settings, json_file, indent=4)
                if not use_database:
                    os.remove(self.database_settings_path)
                    ui.notify('Database configuration removed', color='yellow', type='warning')
                else:
                    database.initialSetup(host=database_host, database=database_name, user=database_user, password=database_pass)
                    ui.notify('Database created/modified', color='green', type='positive')
                ui.notify('Settings saved.', color='green', type='positive')
                logger.log('Settings saved.', 'SUCCESS')
