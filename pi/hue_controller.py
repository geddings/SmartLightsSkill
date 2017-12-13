import os
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class lightArray:
    def __init__(self, name, iot):
        self.name = name

        self.shadow = iot.createShadowHandlerWithName(self.name, True)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)
        self.set(False)

    def set(self, state):
        #hue code to turn on of off light

    def newShadow(self, payload, responseStatus, token):
        newState = json.loads(payload)['state']['light']
        self.set(newState)


def createIoT():
    iot = AWSIoTMQTTShadowClient('MyPi', useWebsocket=True) # I think the first arg is the name of the IoT thing in aws
    iot.configureEndpoint('a7gta1kdqgnmm.iot.us-east-1.amazonaws.com', 443) # REST endpoint
    iot.configureCredentials(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'root-CA.pem')) # CA certificate
    iot.configureConnectDisconnectTimeout(10)  # 10 sec
    iot.configureMQTTOperationTimeout(5)  # 5 sec
    iot.connect()
    return iot


if __name__ == "__main__":
    iot = createIoT()

    lightArray('light-1', iot)