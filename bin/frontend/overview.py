import json, os, threading, time
from nicegui import ui
from backend.data_collection import generalInformation, fritzboxInformation
from backend.gui_logging import Logging

logger = Logging()

class Overview:
    def __init__(self):
        self.settings_dir = 'config'
        self.settings_path = os.path.join(self.settings_dir, 'settings.json')
        self._ensure_settings_dir_exists()
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as json_file:
                settings = json.load(json_file)
                self.address = settings.get('address', '')
                self.username = settings.get('username', '')
                self.password = settings.get('password', '')
                self.domain = settings.get('domain', '')
                self.refresh_interval = settings.get('refresh_interval', '')

    def _ensure_settings_dir_exists(self):
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

    class InfoCards:
        global is_fritzbox_connected, download_speed, upload_speed, is_dns_available
        class IsFritzboxConnected:
            def create(self):
                global is_fritzbox_connected
                with ui.column().style('color: white; background-color:rgba(21, 120, 207, 0.18); border: solid 3px #1577cf; padding: 1em; border-radius: 8px; display: flex; align-items: center; justify-content: center; width: 19em;'):
                    ui.label('Connected to the Internet').style('font-size: 1.25rem; font-weight: bold; color: #1577cf')
                    is_fritzbox_connected = ui.label('Loading...').style('font-size: 2rem; text-align: center; color: #1577cf')
            def set_text(self, text):
                    is_fritzbox_connected.set_text(text)
        class DownloadSpeed:
            def create(self):
                global download_speed
                with ui.column().style('color: white; background-color:rgba(21, 120, 207, 0.18); border: solid 3px #1577cf; padding: 1em; border-radius: 8px; display: flex; align-items: center; justify-content: center; width: 19em;'):
                    ui.label('Download Speed').style('font-size: 1.25rem; font-weight: bold; color: #1577cf')
                    download_speed = ui.label('Loading...').style('font-size: 2rem; text-align: center; color: #1577cf')
            def set_text(self, text):
                download_speed.set_text(text)
        class UploadSpeed:
            def create(self):
                global upload_speed
                with ui.column().style('color: white; background-color:rgba(21, 120, 207, 0.18); border: solid 3px #1577cf; padding: 1em; border-radius: 8px; display: flex; align-items: center; justify-content: center; width: 19em;'):
                    ui.label('Upload Speed').style('font-size: 1.25rem; font-weight: bold; color: #1577cf')
                    upload_speed = ui.label('Loading...').style('font-size: 2rem; text-align: center; color: #1577cf')
            def set_text(self, text):
                upload_speed.set_text(text)
        class DnsAvailability:
            def create(self):
                global is_dns_available
                with ui.column().style('color: white; background-color:rgba(21, 120, 207, 0.18); border: solid 3px #1577cf; padding: 1em; border-radius: 8px; display: flex; align-items: center; justify-content: center; width: 19em;'):
                    ui.label('DNS Availability').style('font-size: 1.25rem; font-weight: bold; color: #1577cf')
                    is_dns_available = ui.label('Loading...').style('font-size: 2rem; text-align: center; color: #1577cf')
            def set_text(self, text):
                    is_dns_available.set_text(text)

        def create_all(self):
            self.IsFritzboxConnected().create()
            self.DnsAvailability().create()
            self.DownloadSpeed().create()
            self.UploadSpeed().create()

        def edit_all(self, value_is_fritzbox_connected, value_download_speed, value_upload_speed, value_is_dns_available):
            try:
                is_fritzbox_connected.set_text(value_is_fritzbox_connected)
                is_dns_available.set_text(value_is_dns_available)
                download_speed.set_text(value_download_speed)
                upload_speed.set_text(value_upload_speed)
            except Exception as e:
                logger.log(f'Error updating info cards: {e}', 'ERROR')
                return False
            else:
                logger.log('Updated info cards with new data', 'SUCCESSFUL')
                return True

    def create(self):
        with ui.column().style('padding: 1em; display: flex;'):
            with ui.grid().classes('p-0 gap-0').style('width: 100%; border-bottom: solid 8px #1577cf; border-bottom-left-radius: 8px; display: flex;'):
                ui.label('Overview').style('font-size: 2rem; font-weight: bold; color: white; padding: 0.25em; background-color: #1577cf; border-radius: 8px 8px 0px 8px; margin-bottom: -8px;')

            with ui.row().style('display: flex; flex-wrap: wrap; justify-content: center; flex-direction: row;'):
                if os.path.exists(self.settings_path):
                    self.InfoCards().create_all()
                    threading.Thread(target=self.refresh_data, daemon=True).start()
                    threading.Thread(target=self.gather_data).start()
                else:
                    self.InfoCards().create_all()
                    ui.notify('Please configure the settings first!', color='red', type='negative', close_button='Understood', timeout=0)
                    logger.log('Please configure the settings first!', 'ERROR')

    def gather_data(self):
        if os.path.exists(self.settings_path):
            logger.log('------------------------------------------')
            logger.log('Collecting data...')
            fritzbox = fritzboxInformation()
            generalInfo = generalInformation()
            try:
                fritzbox.connect(self.address, self.username, self.password)
                try:
                    self.InfoCards().edit_all(
                        str(fritzbox.check_fritzbox_internet_connection()),
                        fritzbox.get_download_speed(),
                        fritzbox.get_upload_speed(),
                        str(generalInfo.checkInternetConnectivity(self.domain))
                        )
                except Exception as e:
                    logger.log(f'Error: {e}', 'ERROR')
                else:
                    logger.log('Collected data', 'SUCCESSFUL')
            except Exception as e:
                logger.log(f'Error connecting to Fritzbox: {e}', 'ERROR')
            else:
                logger.log('Connected to router', 'SUCCESSFUL')

    def refresh_data(self):
        while True:
            with open(self.settings_path, 'r') as json_file:
                settings = json.load(json_file)
                refresh_time = settings.get('refresh_interval', '')
            threading.Thread(target=self.gather_data).start()
            time.sleep(refresh_time)

    def reload(self, refresh_interval):
        self.refresh_interval = refresh_interval
        self.InfoCards.edit_all(self, 'Loading...', 'Loading...', 'Loading...', 'Loading...')
        threading.Thread(target=self.gather_data).start()
