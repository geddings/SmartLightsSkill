import os
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from phue import Bridge


class lightArray:
    lightcheck = "off"
    effectcheck = "none"

    def __init__(self, name, iot):
        self.name = name

        self.shadow = iot.createShadowHandlerWithName(self.name, True)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)
        # self.set(False)

    def set(self, state):
        print(state)
        b = Bridge('192.168.1.128')
        b.connect()

        lightArray.lightcheck = state['lights']
        lightArray.effectcheck = state['effect']

        if state['lights'] == "on":
            if state['effect'] == "blink":
                b.set_light([1, 2], "on", False, transitiontime=0)
                while lightArray.lightcheck == "on" and lightArray.effectcheck != "none":
                    time.sleep(1)
                    b.set_light([1, 2], "on", True, transitiontime=0)
                    time.sleep(1)
                    b.set_light([1, 2], "on", False, transitiontime=0)

            elif state['effect'] == "cycle":
                count = 0
                b.set_light([1, 2], "on", False, transitiontime=0)
                while lightArray.lightcheck == "on" and lightArray.effectcheck != "none":
                    if count%2 == 0:
                        b.set_light(1, "on", True, transitiontime=0)
                        b.set_light(2, "on", False, transitiontime=0)
                    else:
                        b.set_light(1, "on", False, transitiontime=0)
                        b.set_light(2, "on", True, transitiontime=0)
                    count = count + 1
                    time.sleep(1)

            elif state['effect'] == "count":
                count = 0
                count2 = 0
                b.set_light([1, 2], "on", False, transitiontime=0)
                while lightArray.lightcheck == "on" and lightArray.effectcheck != "none":
                    if count % 2 == 0:
                        b.set_light(1, "on", False, transitiontime=0)
                    else:
                        b.set_light(1, "on", True, transitiontime=0)
                    if count2 % 2 == 0:
                        b.set_light(2, "on", False, transitiontime=0)
                    else:
                        b.set_light(2, "on", True, transitiontime=0)
                    count = count + 1
                    if count % 2 == 1:
                        count2 = count2 + 1
                    time.sleep(1)


            else:
                b.set_light([1, 2], "on", True)
        else:
            b.set_light([1, 2], "on", False)

    def newShadow(self, payload, responseStatus, token):
        print(payload)
        newState = json.loads(payload)['state']
        self.set(newState)


def createIoT():
    iot = AWSIoTMQTTShadowClient('RaspberryPi',
                                 useWebsocket=True)  # I think the first arg is the name of the IoT thing in aws
    iot.configureEndpoint('a3lujo7s13ykr5.iot.us-east-1.amazonaws.com', 443)  # REST endpoint
    iot.configureCredentials(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'root-CA.pem'))  # CA certificate
    iot.configureConnectDisconnectTimeout(10)  # 10 sec
    iot.configureMQTTOperationTimeout(5)  # 5 sec
    iot.connect()
    return iot


if __name__ == "__main__":
    iot = createIoT()

    lightArray('RaspberryPi', iot)

    while True:
        time.sleep(.1)
