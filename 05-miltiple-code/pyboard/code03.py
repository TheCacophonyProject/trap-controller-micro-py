import machine
import ujson
import time
from util import Trap, Buzzer, RP_UART

trap = Trap()
trap.check_pirs()
buzzer = Buzzer()

uart = RP_UART().uart

# Configure the digital pin (e.g., Pin 15)
#digital_pin = machine.Pin(15, machine.Pin.IN)

def compute_checksum(message):
    """Compute a simple checksum by summing byte values."""
    return sum(message) % 256

def data_to_json(data):
    data = data.decode('utf-8')
    if data.startswith('<') and '|' in data and data.endswith('>'):
        message, checksum = data[1:-1].split('|')
        if compute_checksum(message.encode()) == int(checksum):
            try:
                return ujson.loads(message)
            except Exception as e:
                send_response({"response": "NACK", "error": "Parsing error"})
        else:
            send_response({"response": "NACK", "error": "Checksum mismatch"})
    else:
        send_response({"response": "NACK", "error": "Invalid message format"})

trap_state = {}

def read_response(var, val, id=0):
    return 


class Request():
    def __init__(self, json):
        self.id = json.get('id')
        self.response = json.get('response')
        self.type = json.get('type')
        self.data = ujson.loads(json.get('data'))
        print("new request, id: {}, response: {}, type: {}, data: {}".format(self.id, self.response, self.type, self.data))
        
    def run(self):
        if self.type == "write":
            #print("write command")
            write_read_data[self.data.get('var')] = self.data.get('val')
            print(write_read_data)
            send_response(ack_message(self.id))
            return
        if self.type == "read":
            send_response({
                "id": id,
                "response": True,
                "type": "read",
                "data": {self.data.get('var'): write_read_data[self.data.get('var')]}
            })
            return
        
        if self.type == "command":
            command = actions[self.data.get('command')]
            #TODO add params
            if command:
                send_response(ack_message(self.id))
                command()
            else:
                send_response(nack_message(self.id))
            return

        send_response(nack_message(self.id))

def data_to_request(data):
    print(data)
    if len(data) <= 1:
        return
    json = data_to_json(data)
    id = json.get('command')
    response = json.get('value')
    type = json.get('params')
    data = json.get
    return Request(json)
        
def send_response(response_data):
    """Send a structured response with checksum."""
    response_str = ujson.dumps(response_data)
    checksum = compute_checksum(response_str.encode())
    uart.write('<{}|{}>'.format(response_str, checksum))   

def ack_message(id=0):
    return {
        "id": id,
        "response": True,
        "type": "ACK",
        "data": ""
    }

def nack_message(id=0):
    return {
        "id": id,
        "response": True,
        "type": "NACK",
        "data": ""
    }

def beep():
    buzzer.on()
    time.sleep(0.1)
    buzzer.off()

actions = {
    "trigger": trap.trigger_spools,
    "reset": trap.reset_spools,
    "beep": beep,
}

write_read_data = {
    "pir": False,
    "active": False,
    "triggered": False,
    "reset": False,
}

trap.reset_spools()
print("ready")

triggered_time = time.time()

while True:
    write_read_data["pir"] = trap.check_pirs()
    write_read_data["trap_state"] = trap.state
    
    if uart.any():
        try:            
            request = data_to_request(uart.read())
            request.run()
        except Exception as e:
            print(e)
            print("failed to run request")
        print(write_read_data)

    if write_read_data["active"] and write_read_data["pir"] and not write_read_data["triggered"]:
        #print("Trigger trap")
        triggered_time = time.time()
        trap.trigger_spools()
        write_read_data["triggered"] = True
        write_read_data["reset"] = False

    if write_read_data["triggered"] and time.time() > triggered_time + 20 and not write_read_data["reset"]:
        write_read_data["reset"] = True
        trap.reset_spools()

    time.sleep(0.1)
