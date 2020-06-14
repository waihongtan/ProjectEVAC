# -*- coding: utf-8 -*-
import time
import Classes

mySensors = Classes.SensorClass()    
dangerCount = 0
valve_start_time = time.time()
try:
    while True:
        #check for flame
        cooking, flamepresence = mySensors.check_flame()[0], mySensors.check_flame()[1]  
        #check for gas
        perc = mySensors.MQPercentage()
        gasVol = mySensors.gasVolume()
        #check for pot
        potpresence = mySensors.check_pot()
        #check for flowrate
        flowrate = mySensors.check_flow()
        
        print("LPG: %g ppm. Gas Volume is %s. %s. %s. Flow rate: %d liters/min \n" % (perc["GAS_LPG"], gasVol, 
                                                            str(flamepresence), str(potpresence), str(flowrate)))
        if gasVol == "high" and cooking == False:
            dangerCount += 1
            print ("Danger")
        else:
            dangerCount = 0
        #Turn off the valve if the danger count is more than 10
        if dangerCount >=1:
            print("Super danger")
            time_elasped = valve_start_time - time.time()
            print("time elapsed: ", time_elasped)
            mySensors.valve_close()
        else:
            mySensors.valve_open()
            valve_start_time = time.time()
        time.sleep(0.5)
        
        """ SENSORS PUBLISH PAYLOADS TO TOPICS """
        #publish the payload on the defined MQTT topic
        mySensors.client.publish("rpi2/sensor/pot", str(potpresence), qos=0, retain=False)
        mySensors.client.publish("rpi2/sensor/flame", str(flamepresence), qos=0, retain=False)
        mySensors.client.publish("rpi2/sensor/flowrate", str(flowrate), qos=0, retain=False)
        
        #on the configuration.yaml file, the corresponding topic for the switch is under state_topic
        mySensors.client.publish("rpi2/switch/gasvalve", str(mySensors.gas_valve_status), qos=0, retain=False)    
        #the blocking call that processes network traffic, dispatches callbacks and handles automatic reconnecting
        mySensors.client.loop_forever()

except KeyboardInterrupt:
    mySensors.valve_close()
    raise        