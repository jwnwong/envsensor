from flask import Flask, request, Response, jsonify, json 
import paho.mqtt.client as mqtt
from time import strftime,sleep,time, localtime
import sqlite3

devices = ['livingroom', 'bedroom']

def handle_mqtt_msg(client, userdata, message):
    global timestamp, temperature, humidity, pressure

    sensorID = message.topic[10:]
    data = json.loads(str(message.payload.decode("utf-8")))
    temperature = data['temperature']
    humidity = data['humidity']
    pressure = data['pressure']
    timestamp = localtime(time())
    
    # write to log file
    with open('DHT.log','a') as f: 
        log_str = sensorID + strftime(",%Y-%m-%d, %H:%M:%S, ",timestamp) + \
            f'{temperature:.2f}, {humidity:.2f}, {pressure:.2f} \n'
        f.write(log_str)
        f.close()

    # write to sqlite database
    connection = sqlite3.connect('dht.db')
    cursor = connection.cursor()        
    update_value = f'"{sensorID}",'+strftime('"%Y-%m-%d","%H:%M:%S",',timestamp) + \
        f'{temperature:.2f}, {humidity:.2f}, {pressure:.2f}'
    sql_update = "insert into dht values(" + update_value + ")"    
    # print(sql_update)
    cursor.execute(sql_update)
    connection.commit()
    cursor.close()
    connection.close()
            

client = mqtt.Client("Server")
print("Connecting to broker server.")
flag_connected = False
while not flag_connected: 
    try:
        client.connect('172.20.97.150')
    except:
        print("Unable to connect to MQTT broker. Will try again later.")
        sleep(5)
    else:
        flag_connected = True
        print("Connected to MQTT broker.")
        client.on_message = handle_mqtt_msg
        client.loop_start() 

for device in devices:          # subscribe to each device to monitor
    client.subscribe('envsensor/'+device)

app = Flask(__name__)

@app.route('/env',methods = ['GET'])
def getSensorValue():
    sensor = request.args.get('sensor')
    if sensor == 'temperature':
        value = temperature
    elif sensor == 'humidity':
        value = humidity
    elif sensor == 'pressure':
        value = pressure
    js = {sensor: round(value,1)}
    return jsonify(js)

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5051, threaded=True)
    
