from collections import deque
import time

class LogManager:
    def __init__(self, max_len=10):
        self.logs = deque(maxlen=max_len)
        # Add initial system log
        self.add_log("INFO", "Sistema Iniciado - Esperando instrucciones")

    def add_log(self, type, message):
        """
        Types: INFO, ALARMA, ERROR, SISTEMA
        """
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            'time': timestamp,
            'type': type,
            'msg': message
        }
        # Avoid duplicate consecutive logs to reduce noise
        if len(self.logs) > 0 and self.logs[0]['msg'] == message and self.logs[0]['type'] == type:
            return 
            
        self.logs.appendleft(entry)

    def get_logs(self):
        return list(self.logs)
