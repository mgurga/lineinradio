import threading
import time as ptime

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer

from .tasks import get_stream_bytes


class RadioConsumer(WebsocketConsumer):
    def stream_bytes(self):
        sec_chunks = 1

        while self.send_chunks:
            ptime.sleep(sec_chunks)
            self.send(bytes_data=get_stream_bytes(sec_chunks=sec_chunks))

    def connect(self):
        self.accept()
        self.send_chunks = True

        self.thread = threading.Thread(target=self.stream_bytes)
        self.thread.start()

    def receive(self, text_data=None, bytes_data=None):
        print(f"radio receieved data: {text_data}")
        self.send(text_data=text_data)

    def disconnect(self, code):
        print("radio disconnected")
        self.send_chunks = False
        raise StopConsumer()
