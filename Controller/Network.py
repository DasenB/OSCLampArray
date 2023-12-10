from pythonosc import udp_client, osc_bundle_builder, osc_message_builder
import time
from collections import deque 

class Network:
    udp_clients: list[udp_client]
    changes: dict[str, int]
    batch_duration_s: float
    last_send_time: float
    history: deque

    def __init__(self, ips: str, port: int, batch_duration_s: float) -> None:
        self.udp_clients = []
        for ip in ips:
            self.udp_clients.append(udp_client.UDPClient(ip, port))
        self.changes = {}
        self.batch_duration_s = batch_duration_s
        self.last_send_time = time.time()
        history_size = 10
        self.history = deque([""] * history_size, maxlen=history_size)

    def add_message(self, path: str, value: int):
        self.changes[path] = value

    def send_batch(self):
        current_time = time.time()
        if self.last_send_time + self.batch_duration_s > current_time:
            return
        if len(self.changes.keys()) == 0:
            self.last_send_time = current_time
            return
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        for path in self.changes.keys():
            message = osc_message_builder.OscMessageBuilder(address=path)
            value = int(self.changes[path])
            message.add_arg(value)
            message = message.build()
            bundle.add_content(message)
            self.history.append(path + " " + str(value))
        bundle = bundle.build()
        for udp in self.udp_clients:
            udp.send(bundle)
        self.last_send_time = current_time
        self.changes = {}