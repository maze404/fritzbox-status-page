import requests
from fritzconnection.lib.fritzstatus import FritzStatus
from .logging import Logging

logger = Logging()

class generalInformation():
    def __init__(self):
        return

    def checkInternetConnectivity(self, checkDomain):
        self.checkDomain = checkDomain
        try:
            response = requests.get("https://" + self.checkDomain, timeout=5)
        except Exception as e:
            logger.log(f'{e}', 'ERROR')
            return False
        else:
            logger.log(f'Domain check for {self.checkDomain} completed: Code {response.status_code}', 'SUCCESSFUL')
            return response.status_code == 200

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
            logger.log(f'{e}', 'ERROR')
            return False

    def check_fritzbox_internet_connection(self):
        try:
            self.fritz_status.is_connected
        except Exception as e:
            logger.log(f'{e}', 'ERROR')
            return False
        else:
            logger.log(f'Router is connected to the internet: {self.fritz_status.is_connected}', 'SUCCESSFUL')
            return True

    def get_download_speed(self):
        try:
            self.fritz_status
        except Exception as e:
            logger.log(f'{e}', 'ERROR')
            return False
        else:
            download_speed_bps = self.fritz_status.max_bit_rate[1]
            download_speed = round(download_speed_bps / 1_000_000)
            logger.log(f'Download speed is: {download_speed_bps} bits/s', 'SUCCESSFUL')
            return download_speed

    def get_upload_speed(self):
        try:
            self.fritz_status
        except Exception as e:
            logger.log(f'{e}', 'ERROR')
            return False
        else:
            upload_speed_bps = self.fritz_status.max_bit_rate[0]
            upload_speed = round(upload_speed_bps / 1_000_000)
            logger.log(f'Upload speed is: {upload_speed_bps} bits/s', 'SUCCESSFUL')
            return upload_speed
