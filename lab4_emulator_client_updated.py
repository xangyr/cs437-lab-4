# Import SDK packages
import time

import pandas as pd
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Starting and end index, modify this
device_st = 0
device_end = 5

# Path to the dataset, modify this
data_path = "data2/vehicle{}.csv"

# Path to your certificates, modify this
certificate_formatter = "./certificates/device_{}/device_{}.cert.pem"
key_formatter = "./certificates/device_{}/device_{}.private.pem"

topic = "emission/car/trigger"


class MQTTClient:
    def __init__(self, device_id, cert, key):
        # For certificate based connection
        self.device_id = str(device_id)
        self.state = 0
        self.client = AWSIoTMQTTClient(self.device_id)

        self.client.configureEndpoint("a2ps877ygecemo-ats.iot.us-west-2.amazonaws.com", 8883)
        self.client.configureCredentials("./AmazonRootCA1.pem.txt", key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage

    def customOnMessage(self, message):
        print("client {} received payload {} from topic {}".format(self.device_id, message.payload, message.topic))

    # Suback callback
    def customSubackCallback(self, mid, data):
        # You don't need to write anything here
        pass

    # Puback callback
    def customPubackCallback(self, mid):
        # You don't need to write anything here
        pass

    def publish(self, Payload="payload"):
        self.client.subscribeAsync(topic, 0, ackCallback=self.customSubackCallback)

        self.client.publishAsync(topic, Payload, 0, ackCallback=self.customPubackCallback)


print("Loading vehicle data...")
data = []
for i in range(5):
    a = pd.read_csv(data_path.format(i))
    data.append(a)

print("Initializing MQTTClients...")
clients = []
for device_id in range(device_st, device_end):
    client = MQTTClient(device_id, certificate_formatter.format(device_id, device_id),
                        key_formatter.format(device_id, device_id))
    client.client.connect()
    clients.append(client)

while True:
    print("send now?")
    x = input()
    if x == "s":
        for i, c in enumerate(clients):
            c.publish('Testing messages')

    elif x == "d":
        for c in clients:
            c.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("wrong key pressed")

    time.sleep(3)
