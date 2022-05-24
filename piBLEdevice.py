
#ubit_address = 'E5:10:5E:37:11:2d'
#ubit_address = 'E0:E2:E6:9D:0F:Da'
#E0:E2:E6:9D:0F:DA
import BLE_GATT
from gi.repository import GLib

ubit_address = 'E0:E2:E6:9D:0F:DA'
uart_rx = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
uart_tx = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'


def notify_handler(value):
    print(f"Received: {bytes(value).decode('UTF-8')}")


def send_ping():
    print('sending: ping')
    ubit.char_write(uart_rx, b'ping\n')
    return True


ubit = BLE_GATT.Central(ubit_address)
ubit.connect()
ubit.on_value_change(uart_tx, notify_handler)
GLib.timeout_add_seconds(20, send_ping)
ubit.wait_for_notifications()