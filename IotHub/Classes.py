###MODULES TO INPUT GOES HERE
import RPi.GPIO as GPIO
import time
#import sys
import math
from MCP3008 import MCP3008

import paho.mqtt.client as paho

broker = "10.12.108.241"
port = 1883
#keepalive: maximum period in seconds allowed between communications with the broker. 
#If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker
keepalive = 60

###GPIO SETUP
print("Setting up gpio...")
GPIO.setmode(GPIO.BCM)
FLAME = 21    #flame sensor 
VALVE = 20    #gas valve 
IR = 17       #IR sensor (pot)
FLOW = 22     #flow sensor 
GPIO.setup(FLAME, GPIO.IN)
GPIO.setup(VALVE, GPIO.OUT)
GPIO.setup(IR,GPIO.IN)
GPIO.setup(FLOW,GPIO.IN)

###Initalization of Variables
cooking = False
GPIO.output(VALVE, 0) #open the valve

class MQTTClient():
         
    def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribed to topic : " + str(mid) + " with Qos " + str(granted_qos))
        pass

    def on_publish(client, userdata, mid):
        print("Published to topic: " + str(mid) + "\n")
        pass

    def on_connect(client, userdata, flags, rc):
        client.subscribe("rpi1/switch/gasvalve", 0)
        print("Connected to MQTT broker with result code: " + str(rc) + "\n")
        pass 
    
    def on_disconnect(client, userdata, rc):
        if rc!=0:
            print("Unexpected disconnection") 
            pass
       
    def on_message(client, userdata, msg):
        print("Received message: on topic " + str(msg.topic) 
        + " " + "with QoS " + str(msg.qos))    
        
        if str(msg.payload.decode()) == "OFF":
            GPIO.output(VALVE, 0)
            
        if str(msg.payload.decode()) == "ON":
            GPIO.output(VALVE, 1)
        
    client = paho.Client("rpi_pub", clean_session= False, userdata=None)
    #assign the functions to the respective callbacks 
    client.on_publish= on_publish
    client.on_message= on_message
    client.on_connect= on_connect
    client.on_disconnect= on_disconnect
    #set a username and password for broker authentification
    client.username_pw_set("projectalfred", "projectalfred")
    #client.max_inflight_messages.set()
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    #establish connection to the broker
    client.connect(broker, port, keepalive)
    

class SensorClass(MQTTClient):
    
    ###########################
    ### CODE FOR MQ6 sensor ###
    ###########################

    ######################### Hardware Related Macros #########################
    MQ_PIN                       = 0        # define which analog input channel you are going to use (MCP3008)
    RL_VALUE                     = 5        # define the load resistance on the board, in kilo ohms
    RO_CLEAN_AIR_FACTOR          = 9.83     # RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
                                            # which is derived from the chart in datasheet
 
    ######################### Software Related Macros #########################
    CALIBARAION_SAMPLE_TIMES     = 5       # define how many samples you are going to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL  = 500      # define the time interval(in milisecond) between each samples in the
                                            # cablibration phase
    READ_SAMPLE_INTERVAL         = 5       # define the time interval(in milisecond) between each samples in
    READ_SAMPLE_TIMES            = 1        # define how many samples you are going to take in normal operation 
                                            # normal operation
 
    ######################### Application Related Macros ######################
    GAS_LPG                      = 0
    #GAS_CO                       = 1 #redundant at the moment
    #GAS_SMOKE                    = 2 #redundant at the moment

    def __init__(self, Ro=10, analogPin=0, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        self.Ro = Ro
        self.MQ_PIN = analogPin
        self.adc = MCP3008()
        self.LPGCurve = [2.3,0.21,-0.47]    # two points are taken from the curve. 
                                            # with these two points, a line is formed which is "approximately equivalent"
                                            # to the original curve. 
                                            # data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59) 
        print("Calibrating...")
        self.Ro = self.MQCalibration(self.MQ_PIN)
        print("Calibration is done...\n")

    def MQPercentage(self):
        val = {}
        read = max(self.MQRead(self.MQ_PIN),0.0001)
        val["GAS_LPG"]  = self.MQGetGasPercentage(read/self.Ro, self.GAS_LPG)
        '''To enable the values for other type of gas, uncomment the code below'''
        #val["CO"]       = self.MQGetGasPercentage(read/self.Ro, self.GAS_CO)
        #val["SMOKE"]    = self.MQGetGasPercentage(read/self.Ro, self.GAS_SMOKE)
        '''The code above is commented as it is not function intended for use'''
        return val

    def MQResistanceCalculation(self, raw_adc):
        return float(self.RL_VALUE*(1023.0-raw_adc)/float(raw_adc));
     
    def MQCalibration(self, mq_pin):
        val = 0.0
        for i in range(self.CALIBARAION_SAMPLE_TIMES):          # take multiple samples
            val += self.MQResistanceCalculation(self.adc.read(mq_pin))
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000.0)
        val = val/self.CALIBARAION_SAMPLE_TIMES                 # calculate the average value
        val = val/self.RO_CLEAN_AIR_FACTOR                      # divided by RO_CLEAN_AIR_FACTOR yields the Ro 
                                                                # according to the chart in the datasheet 
        return val
      
    def MQRead(self, mq_pin):
        rs = 0.0
        for i in range(self.READ_SAMPLE_TIMES):
            rs += self.MQResistanceCalculation(self.adc.read(mq_pin))
            time.sleep(self.READ_SAMPLE_INTERVAL/1000.0)
        rs = rs/self.READ_SAMPLE_TIMES
        return rs

    def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
        if ( gas_id == self.GAS_LPG ):
            return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
        '''To enable the values for other type of gas, uncomment the code below'''
        #elif ( gas_id == self.GAS_CO ):
        #    return self.MQGetPercentage(rs_ro_ratio, self.COCurve)
        #elif ( gas_id == self.GAS_SMOKE ):
        #    return self.MQGetPercentage(rs_ro_ratio, self.SmokeCurve)
        '''The code above is commented as it is not function intended for use'''
        return 0

    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        return (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/ pcurve[2]) + pcurve[0])))
    
    def gasVolume(self):
        '''This function determine if the LPG gas percentage is HIGH or LOW
        change the variable 'threshold_gas' to adjust the threshold.
        
        To display the raw value, use self.MQPercentage().get('GAS LPG') instead'''
        
        threshold_gas = 10 #determines the sensitivity of MQ sensor
        
        if self.MQPercentage().get('GAS_LPG') > threshold_gas:
            return "high"
        else: 
            return "low"
    
    #############################
    ### CODE FOR FLAME SENSOR ###
    #############################
    '''Version 1: This version will change the value whenever there is a change in the GPIO pin input. Good for saving computation time.
    def check_flame():
        #print ("Flame is now",flame_detect)
        if flame_detect == True:
            print ("Flame detected!")
            cooking = True
        else:
            cooking = False
        return flame_detect
    
    def callback(FLAME):
        global flame_detect
        if not(GPIO.input(FLAME)): #if pin is HIGH
            print("Flame detected")
            flame_detect = True
        else:
            print("No flame detected")
            flame_detect = False
    GPIO.add_event_detect(FLAME, GPIO.BOTH)  # let us know when the pin goes HIGH or LOW
    GPIO.add_event_callback(FLAME, callback)  # assign function to GPIO PIN,Run function on change'''
    
    '''Version2: This version checks the GPIO pin input each time it is called. Good for integrating with other scripts'''
    def check_flame():
        flame_result = []
        global cooking
        if not(GPIO.input(FLAME)): #if pin is HIGH
            print("Flame detected")
            cooking = True
            flame_result.append(cooking)
            flame_result.append("Flame is detected.")
        else:
            print("No flame detected")
            cooking = False
            flame_result.append(cooking)
            flame_result.append("No flame.")
        return flame_result
    
        #########################
        ### CODE FOR IR SENSOR###
        #########################

    '''NOTE: The IR sensor only work in the direction directly above the LEDs tips.'''
    def check_pot():
        if GPIO.input(IR): #If the IR pin gives a high input -- pot ABSENT
            print ("No Pot!")
            pot_result = "No Pot!"
        else:
            print ("Pot detected!")
            pot_result = "Pot detected!"
            
        return pot_result
    
        ######################
        ### CODE FOR VALVE ###
        ######################
    
    gas_valve_status = "OFF"
    
    '''NOTE: Do not open the solenoid valve for more than 20 mins. It will damage the solenoid'''
    def valve_open():
        global gas_valve_status 
        gas_valve_status= "ON"
        GPIO.output(VALVE, 1)
    
    def valve_close():
        global gas_valve_status
        gas_valve_status = "OFF"
        GPIO.output(VALVE, 0)
        
        ############################
        ### CODE FOR FLOW SENSOR ###
        ############################
    def check_flow():
        rate_cnt = 0
        tot_cnt = 0
        constant = 0.06
        time_new = 0.0
    
        while True:
            time_new = time.time() + 1
            rate_cnt = 0
            while time.time() <= time_new:
                if GPIO.input(FLOW)== 0:
                    rate_cnt += 1
                    tot_cnt += 1
                '''For Debugging: Uncomment this to show the raw input from the GPIO pin'''
                #print(GPIO.input(FLOW), end='')
                '''0 indicate a revolution of the hall sensor. Something is wrong if the flow rate exceeds 40 liters/min'''
            print('\nLiters / min',round(rate_cnt * constant,4))
            print('Total liters', round(tot_cnt * constant,4))
        flow_litre_min = round(rate_cnt* constant,4)
    
        return flow_litre_min
    
#############################################################################################################               