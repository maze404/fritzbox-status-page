import time, os

class Logging:
    def __init__(self, log_dir='log', max_size=5 * 1024 * 1024, backup_count=5):
        self.log_dir = log_dir
        self.max_size = max_size
        self.backup_count = backup_count
        self._ensure_log_dir_exists()
        self.log_file = os.path.join(self.log_dir, f'log_{time.strftime("%Y-%m-%d")}.txt')

    def _ensure_log_dir_exists(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, message: str, status: str = 'INFO'):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_message = f'[{timestamp}] [{status}] {message}\n'
        self._rotate_logs()
        with open(self.log_file, 'a') as log_file:
            log_file.write(log_message)

    def _rotate_logs(self):
        if os.path.exists(self.log_file) and os.path.getsize(self.log_file) >= self.max_size:
            for i in range(self.backup_count - 1, 0, -1):
                src = f'{self.log_file}.{i}'
                dst = f'{self.log_file}.{i + 1}'
                if os.path.exists(src):
                    os.rename(src, dst)
            os.rename(self.log_file, f'{self.log_file}.1')