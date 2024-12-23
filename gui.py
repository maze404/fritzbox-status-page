import requests, json, os, threading, re, time
from nicegui import ui
from fritzconnection.lib.fritzstatus import FritzStatus

ui.add_head_html('<link rel="preconnect" href="https://fonts.googleapis.com">')
ui.add_head_html('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">')

class generalInformation():
    def __init__(self):
        return

    def checkInternetConnectivity(self, checkDomain):
        self.checkDomain = checkDomain
        try:
            response = requests.get("https://" + self.checkDomain, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

class fritzboxInformation:
    def __init__(self):
        self.fritz_status = None

    def connect(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        try:
            self.fritz_status = FritzStatus(
                address=self.address,
                user=self.username,
                password=self.password
            )
            return True
        except Exception as e:
            return False

    def check_fritzbox_internet_connection(self):
        return self.fritz_status.is_connected

    def get_download_speed(self):
        if not self.fritz_status:
            raise ValueError("Please connect to FritzBox first.")
        download_speed_bps = self.fritz_status.max_bit_rate[1]
        download_speed = round(download_speed_bps / 1_000_000)
        return download_speed

    def get_upload_speed(self):
        if not self.fritz_status:
            raise ValueError("Please connect to FritzBox first.")
        upload_speed_bps = self.fritz_status.max_bit_rate[0]
        upload_speed = round(upload_speed_bps / 1_000_000)
        return upload_speed

class Homepage:
    def __init__(self):
        self.sidebar = None
        self.main_content = None
        self.page_title = "Overview"
        self.refresh_interval = 60  # Default refresh interval

    def create_frame(self):
        background_data_collection = threading.Thread(target=self.gather_data)
        background_data_collection.daemon = True
        background_data_collection.start()
        with ui.row().classes('p-0 gap-0').style('display: inline-flex; width: 100vw;'):
            self.create_sidebar(self.create_frame)
            self.create_main_content(self.create_frame)

    def create_sidebar(self, parent):
        with ui.column().style('background-image: linear-gradient(180deg, #1577cf, #004482); width: 250px; height: 100vh; padding: 1em; flex-shrink: 0; font-family: "Source Sans 3";'):
            ui.image('https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png').style('width: 50%; margin: 0 auto 0 auto; display: block')
            ui.label('FRITZ!Box Status Page').style('color: white; font-size: 2rem; font-weight: bold; margin-bottom: 20px; text-align: left;')
            ui.button('Home').style('width: 100%; display: flex; justify-content: flex-start;')
            #ui.button('Settings').style('width: 100%; display: flex; justify-content: flex-start;')

    def create_main_content(self, parent):
        with ui.column().style('padding: 1em; overflow-y: auto; display: flex; max-height: 100vh; max-width: calc(100% - 250px); font-family: "Source Sans 3"; align-items: center;'):
            ui.label(self.page_title).style('font-size: 2rem; font-weight: bold; margin-bottom: 20px; color: white;')
            self.create_overview(self.create_main_content)
            self.create_settings(self.create_main_content)

    def create_overview(self, parent):
        with ui.row().style('max-width: calc(100%-250px); font-family: "Source Sans 3";'):
            if os.path.exists('settings.json'):
                labels = [
                    ('Connected to the Internet', 'is_fritzbox_connected'),
                    ('Download Speed (Mbps)', 'download_speed'),
                    ('Upload Speed (Mbps)', 'upload_speed'),
                    ('DNS functional', 'is_dns_available')
                ]
                for label_text, attr_name in labels:
                    with ui.column().style('color: white; background-color: #333; padding: 1em; border-radius: 8px; display: flex; align-items: center; justify-content: center;'):
                        ui.label(label_text).style('font-size: 1.25rem; font-weight: bold;')
                        setattr(self, attr_name, ui.label('Loading...').style('font-size: 2rem; text-align: center;'))

    def gather_data(self):
        while True:
            fritzbox = fritzboxInformation()
            with open('settings.json', 'r') as json_file:
                settings = json.load(json_file)
                self.address = settings.get('address', '')
                self.username = settings.get('username', '')
                self.password = settings.get('password', '')
                self.domain = settings.get('domain', '')
                fritzbox = fritzboxInformation()
                generalInfo = generalInformation()
                if fritzbox.connect(self.address, self.username, self.password):
                    self.is_fritzbox_connected.set_text(str(fritzbox.check_fritzbox_internet_connection()))
                    self.download_speed.set_text(str(fritzbox.get_download_speed()))
                    self.upload_speed.set_text(str(fritzbox.get_upload_speed()))
                else:
                    self.is_fritzbox_connected.set_text("Error: Unable to connect to FRITZ!Box")
                    self.download_speed.set_text("Error: Unable to connect to FRITZ!Box")
                    self.upload_speed.set_text("Error: Unable to connect to FRITZ!Box")
            self.is_dns_available.set_text(str(generalInfo.checkInternetConnectivity(self.domain)))
            time.sleep(self.refresh_interval)

    def create_settings(self, parent):
        def create_input_row(label_text, input_style, value='', password=False):
            with ui.row().style('background-color: #333; color: white; padding: 1em; border-radius: 8px; align-items: center; width: 100%; font-family: "Source Sans 3"; display: flex;'):
                ui.label(label_text).style('font-size: 1.25rem; font-weight: bold;')
                if password:
                    input_field = ui.input(value=value, password=password, password_toggle_button=True).style(input_style)
                else:
                    input_field = ui.input(value=value, password=password).style(input_style)
                return input_field

        with ui.column().style('background-color: #222; border-radius: 8px; padding: 1em; flex-shrink: 1; max-width: 75vw; overflow-y: auto; display: flex; font-family: "Source Sans 3";'):
            ui.label('Settings').style('font-size: 2rem; font-weight: bold; margin-bottom: 20px; color: white;')
            with ui.row().style('gap: 1em;'):
                if os.path.exists('settings.json'):
                    with open('settings.json', 'r') as json_file:
                        settings = json.load(json_file)
                        address_value = settings.get('address', '')
                        username_value = settings.get('username', '')
                        password_value = settings.get('password', '')
                        domain_value = settings.get('domain', '')
                else:
                    address_value = ''
                    username_value = ''
                    password_value = ''
                    domain_value = ''

                address = create_input_row('Fritz!Box IP', 'font-size: 1.25rem; text-align: center; color: white;', address_value)
                username = create_input_row('Fritz!Box User', 'font-size: 1.25rem; text-align: center; color: white;', username_value)
                password = create_input_row('Fritz!Box Password', 'font-size: 1.25rem; text-align: center; color: white;', password_value, password=True)
                domain = create_input_row('Check Domain', 'font-size: 1.25rem; text-align: center; color: white;', domain_value)
                ui.label('Overview Refresh Interval (seconds)').style('font-size: 1.25rem; font-weight: bold; color: white;')
                refresh_interval_slider = ui.slider(min=5, max=600, value=self.refresh_interval).style('width: 100%;')
                refresh_interval_label = ui.label(f'{self.refresh_interval} seconds').style('font-size: 1rem; color: white;')
                refresh_interval_slider.on_value_change(lambda: refresh_interval_label.set_text(f'{refresh_interval_slider.value} seconds'))
            ui.button('Save').style('width: 100%; display: flex; justify-content: flex-start;').on_click(lambda: self.save_settings(address.value, username.value, password.value, domain.value, refresh_interval_slider.value))

    def save_settings(self, address, username, password, domain, refresh_interval):
        if not address:
            ui.notify('IP address cannot be empty', color='red')
            return
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', address):
            ui.notify('Invalid IP address format', color='red')
            return
        if not username:
            ui.notify('Username cannot be empty', color='red')
            return
        if not re.match(r'^[\w-]+$', username):
            ui.notify('Username can only contain letters, digits, underscores, and hyphens', color='red')
            return
        if not password:
            ui.notify('Password cannot be empty', color='red')
            return
        if len(password) < 8:
            ui.notify('Password must be at least 8 characters long', color='red')
            return
        if not domain:
            ui.notify('Domain cannot be empty', color='red')
            return
        if not re.match(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$', domain):
            ui.notify('Invalid domain format', color='red')
            return

        settings = {
            'address': address,
            'username': username,
            'password': password,
            'domain': domain,
            'refresh_interval': refresh_interval
        }
        if os.path.exists('settings.json'):
            os.remove('settings.json')
        with open('settings.json', 'w') as json_file:
            json.dump(settings, json_file, indent=4)
        self.refresh_interval = refresh_interval
        self.is_fritzbox_connected.set_text('Loading...')
        self.download_speed.set_text('Loading...')
        self.upload_speed.set_text('Loading...')
        self.is_dns_available.set_text('Loading...')
        background_data_collection = threading.Thread(target=self.gather_data)
        background_data_collection.start()
        ui.notify('Settings saved', color='green')

Homepage().create_frame()
ui.query('.nicegui-content').style('display: flex; margin: 0; padding: 0;')
ui.dark_mode(True)
ui.run(favicon='https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png', title='FRITZ!Box Status Page')