from time import sleep
from random import seed, random, randint
import paho.mqtt.client as mqtt

# Add in your DEVICE ID, DEVICE TYPE, AUTHENTIFICATION TOKEN, ORGANIZATION ID 
# when you add a new device on IBM Watson IoT Platform 
ORG = "7cd6ta"
DEVICE_TYPE = "ubuntu" 
TOKEN = "aOvBQ2hgfZ5oig0TWu"
DEVICE_ID = "e4a471745ee1"
server = ORG + ".messaging.internetofthings.ibmcloud.com"

# TOPIC FORMAT 
#iot-2/evt/{event_name}/fmt/{format_string}
pubTopic1 = "iot-2/evt/temp/fmt/json"
pubTopic2 = "iot-2/evt/humid/fmt/json"
pubTopic3 = "iot-2/evt/gas/fmt/json"
 
subTopic = "iot-2/type/+/id/+/evt/+/fmt/+";
authMethod = "use-token-auth"
token = TOKEN
clientId = "d:" + ORG + ":" + DEVICE_TYPE + ":" + DEVICE_ID

# initialize a seed generator 
seed(4)

# initialize the MQTT client
mqttc = mqtt.Client(client_id=clientId)
mqttc.username_pw_set(authMethod, token)
mqttc.connect(server, 1883, 60)

while True:
    #generate randomized values for each of the three variables 
    humidity, temperature, gasvalue  = random(), randint(0, 100), randint(0, 100)
    print("\nHumidity: ", str(humidity))
    print("Temperature: ", str(temperature))
    print("Gas Value: ", str(gasvalue))

    # publish values to relevant publisher topics 
    mqttc.publish(pubTopic1, temperature)
    mqttc.publish(pubTopic2, humidity)
    mqttc.publish(pubTopic3, gasvalue)
    print("Published")
    sleep(5)

# loop forever until an interrupt or error 
mqttc.loop_forever()
