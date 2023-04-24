
# SORTING PLAYING CARDS
# Cards with face upwards in one pile
# Cards with back upwards in another pile
# Pictures taken with iPhone 12 via Edge Impulse platform
# Using Silicon Labs xG24 Dev Kit + Arducam

# Edge Impulse link : https://studio.edgeimpulse.com/studio/193509
# Name              : xG24 Card colour sorting


from serial.tools import list_ports

import pydobot, serial, threading
import time
import os

#global label

label     = ''
labels    = ["back:", "black:", "no_card:", "red:"]

norm_speed = 1500
norm_acc   = 100

start_z    = -70.8
home_x     = 159
home_y     = -157

cards_lifted = 0                                        # How many cards have we lifted (= tried to lift!)
infer_runs = 0

com_port = "COM14"

#SerialObj = serial.Serial(com_port, 115200) 

available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = "COM10" # available_ports[0].device

use_Dobot = True
if use_Dobot:
    device = pydobot.Dobot(port=port, verbose=False)
    device.speed(norm_speed, norm_acc)

    (x, y, z, r, j1, j2, j3, j4) = device.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')


def open_serial():
    global SerialObj
    
    at_cmd = "AT+RUNIMPULSEDEBUG=USEMAXRATE\r\n"
    at_cmd = "AT+RUNIMPULSECONT\r\n"
    
    try:
        SerialObj = serial.Serial(com_port, 115200)
        print ("Port is open")
        SerialObj.write(b"AT+RUNIMPULSE\r\n")
        time.sleep(1)

    except serial.SerialException:
        SerialObj.Serial(com_port, 115200).close()
        print ("Port is closed")
        SerialObj = SerialObj.Serial(com_port,115200)
        SerialObj.timeout = 0 # set the Read Timeout
        print ("Port is open again")
        print ("Ready to use")
        SerialObj.write(b"AT+RUNIMPULSE\r\n")
        time.sleep(1)

open_serial()



def inference():
    global infer_runs
    
    infer_runs += 1
#    print(f"Inference nr: {infer_runs:<4} Cards lifted: {cards_lifted:<4}")
    

    def read_ln():
        read = SerialObj.readline()
        read = read.decode('utf-8')
        return read.strip()
    

    def find_highest(lines):
        import re
        
        # Define a regular expression pattern to match the label and its score
        pattern = r'\s*(\w+):\s*([\d\.]+)'

        # Initialize variables to store the highest label and score found
        highest_label = None
        highest_score = 0.0

        # Split the serial output into lines
        # lines = serial_output.strip().split('\n')

        # Loop through each line of the serial output
        for line in lines:
            if line.strip() != "":
                ln = line.split()
 #               if ln[0] in labels:
 #                   print (ln)
            # Use regular expression to match the label and its score
            match = re.match(pattern, line)
            if match:
                label = match.group(1)
                score = float(match.group(2))
                # Check if this score is the highest found so far
                if score > highest_score:
                    highest_score = score
                    highest_label = label

        # Print the highest label and its score
        #print(f"Highest label: {highest_label}, score: {highest_score}")
        return highest_label, highest_score

    label_amount = len(labels)
    ln =[""] * (label_amount + 3)
    rows2read = label_amount + 3
    for i in range(rows2read):                          # first reading all lines as fast as possible from serial buffer...
        ln[i] = read_ln()

    lbl_list = find_highest(ln)
    return lbl_list
    



def wait(ms):
    device.wait(ms)

def suction_on():
    device.suck(True)
    
def suction_off():
    device.suck(False)

def left45(leftwait):
    device.move_to(90, 150, start_z + 10, r, wait=leftwait)
    suction_off()
    up(leftwait)
    
def right45(rightwait):
    device.move_to(190, -9, start_z + 10, r, wait=rightwait)
    suction_off()
    up(rightwait)
    
def right22_5(rwait):
    device.move_to(145, 205, start_z + 10, r, wait=rwait)
    suction_off()
    up(rwait)
    
def up(upwait):
    device.move_to(home_x, home_y, -10, r, wait=upwait)
    #inference()

def down(downwait):
    device.move_to(home_x, home_y, start_z - (cards_lifted * 0.325), r, wait=downwait)
    
    
def lift(liftwait):
    global cards_lifted
    
    suction_on()
    cards_lifted += 1
    down(liftwait)
    up(liftwait)
    
   

def main():
    global x,y,z,r,j1,j2,j3,j4
    
    only_inference = False
    while only_inference == True:
        label = inference()
        #time.sleep(.1)
        if label[0]:
            print(f"\t", label[0].upper(), label[1])
        else:
            print(f"\t\t\t\t", label)  
    
    device.suck(False)
    up(True)
       
    while True:
        (x, y, z, r, j1, j2, j3, j4) = device.pose()

        label = ""
    #    SerialObj.read_all()
        SerialObj.flushInput()
        label_lst = inference()
        label = label_lst[0]
        print(label)
        
        if label == "black":
            print("lifting black")
            lift(True)
            right45(False)
        elif label == "red":
            print("lifting red")
            lift(True)
            left45(False)
        elif label == "back":
            print("lifting back")
            lift(True)
            right22_5(False)
        elif label == "no_card":
            print("lifting no card")
        # else:
        #     print("uncertain")

    device.close()

if __name__ == "__main__":
    main()


