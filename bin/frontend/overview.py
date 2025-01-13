import json, os, threading, time
from nicegui import ui
from backend.data_collection import generalInformation, fritzboxInformation
from backend.gui_logging import Logging
from backend.database import MySQLDatabase, SQLiteDatabase, EnvironmentVariables

logger = Logging()
sqldb = SQLiteDatabase()
mysql = MySQLDatabase()

class Overview:
    def __init__(self):
        self.database_path = str(os.path.join("config", "database.db"))
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

        if self.db_mode == 'sqlite':
            self.database_path = str(os.path.join("config", "database.db"))
            sqldb.connect(self.database_path)
            self.address = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_address'")[0]
            self.username = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_user'")[0]
            self.password = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'fritzbox_password'")[0]
            self.domain = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'dns_check_domain'")[0]
            self.refresh_interval = sqldb.fetch_one("SELECT value FROM settings WHERE name LIKE 'refresh_interval'")[0]
            sqldb.disconnect()

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
                if os.path.exists(self.database_path):
                    self.InfoCards().create_all()
                    threading.Thread(target=self.refresh_data, daemon=True).start()
                    threading.Thread(target=self.gather_data).start()
                else:
                    self.InfoCards().create_all()
                    ui.notify('Please configure the settings first!', color='red', type='negative', close_button='Understood', timeout=0)
                    logger.log('Please configure the settings first!', 'ERROR')

    def gather_data(self):
        if os.path.exists(self.database_path):
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
            refresh_time = int(self.refresh_interval)
            threading.Thread(target=self.gather_data).start()
            time.sleep(refresh_time)

    def reload(self, refresh_interval):
        self.refresh_interval = refresh_interval
        self.InfoCards.edit_all(self, 'Loading...', 'Loading...', 'Loading...', 'Loading...')
        threading.Thread(target=self.gather_data).start()
