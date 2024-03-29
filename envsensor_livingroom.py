import paho.mqtt.client as mqtt
from time import sleep
import bme280
import json

temperature = 0
humidity = 0
pressure = 0
exitflag = False
device_ID = "livingroom"
mqtt_address = "0.0.0.0"        


client = mqtt.Client(device_ID)
#client.connect(mqtt_address, port=1883, keepalive=300)
        
while not exitflag:
    temperature, pressure, humidity = bme280.readBME280All()

    # send msg to MQTT broker
    try:
        client.connect(mqtt_address)
    except:
        print("Unable to connect to MQTT broker. Will try again later.")
    else:
        sensorData = json.dumps(
            {"temperature": round(temperature,2),
             "pressure":    round(pressure,2),
             "humidity":    round(humidity,2)
            })
        r = client.publish('envsensor/'+device_ID, payload = sensorData)
            
    sleep(60) 
