import json, os, re
from nicegui import ui
from backend.logging import Logging
from frontend.overview import Overview

logger = Logging()

class Settings:
    def __init__(self):
        self.settings_dir = 'config'
        self.settings_path = os.path.join(self.settings_dir, 'settings.json')
        self._ensure_settings_dir_exists()

    def _ensure_settings_dir_exists(self):
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

    def create(self):
        def create_settings_item(label_text, value, password_field=False):
            with ui.row().style('margin-bottom: 20px; display: flex; align-items: center;'):
                ui.label(label_text).style('font-size: 1.25rem; font-weight: bold; width: 10em')
                input_field = ui.input(value=value, password=password_field, password_toggle_button=password_field).style('font-size: 1.25rem; text-align: center; color: white; width: 15em;')
            return input_field

        with ui.column().style('padding: 1em; display: flex;'):
            with ui.grid().classes('p-0 gap-0').style('width: 100%; border-bottom: solid 8px #1577cf; border-bottom-left-radius: 8px; display: flex;'):
                ui.label('Settings').style('font-size: 2rem; font-weight: bold; color: white; padding: 0.25em; background-color: #1577cf; border-radius: 8px 8px 0px 8px; margin-bottom: -8px;')
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
                    ui.label('Overview Refresh Interval (seconds)').style('font-size: 1.25rem; font-weight: bold; color: white;')
                    refresh_interval_slider = ui.slider(min=5, max=600, value=refresh_interval).style('width: 100%;')
                    refresh_interval_label = ui.label(f'{refresh_interval} seconds').style('font-size: 1rem; color: white;')
                    refresh_interval_slider.on_value_change(lambda: refresh_interval_label.set_text(f'{refresh_interval_slider.value} seconds'))
                    ui.button('Save').style('width: 100%; display: flex; justify_content: flex-start;').on_click(lambda: self.save_settings(address.value, username.value, password.value, domain.value, refresh_interval_slider.value))

    def save_settings(self, address: str, username: str, password: str, domain: str, refresh_interval):
        if not address:
            ui.notify('IP address cannot be empty', color='red', type='negative')
            logger.log('IP address cannot be empty', 'ERROR')
            return
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', address):
            ui.notify('Invalid IP address format', color='red', type='negative')
            logger.log('Invalid IP address format', 'ERROR')
            return
        if not username:
            ui.notify('Username cannot be empty', color='red', type='negative')
            logger.log('Username cannot be empty', 'ERROR')
            return
        if not re.match(r'^[\w-]+$', username):
            ui.notify('Username can only contain letters, digits, underscores, and hyphens', color='red', type='negative')
            logger.log('Username can only contain letters, digits, underscores, and hyphens', 'ERROR')
            return
        if not password:
            ui.notify('Password cannot be empty', color='red', type='negative')
            logger.log('Password cannot be empty', 'ERROR')
            return
        if len(password) < 8:
            ui.notify('Password must be at least 8 characters long', color='red', type='negative')
            logger.log('Password must be at least 8 characters long', 'ERROR')
            return
        if not domain:
            ui.notify('Domain cannot be empty', color='red', type='negative')
            logger.log('Domain cannot be empty', 'ERROR')
            return
        if not re.match(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$', domain):
            ui.notify('Invalid domain format', color='red', type='negative')
            logger.log('Invalid domain format', 'ERROR')
            return
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
