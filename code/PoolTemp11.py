import os
import glob
import time
from time import sleep
import sys
import mariadb
import RPi.GPIO as GPIO
from rpi_lcd import LCD
import datetime
from datetime import date


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

pumpmanual = 0    #Initialise Manual Interrupt Switch
pumpstandby = 0   #Initialise Standby Interrupt Switch
lcdline4 = " "
pumpstate = "Off"
pumpOn = GPIO.LOW
pumpOff = GPIO.HIGH

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, pumpOff)   #Initalise Pump to Off
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Inititalise LCD

GPIO.output(20, GPIO.HIGH)
time.sleep(1)
lcd = LCD()

# Temperature Sensors - code sourced from https://www.circuitbasics.com/
base_dir = '/sys/bus/w1/devices/'
device_folder_roof = glob.glob(base_dir + '28-031297798293')[0]
device_file_roof = device_folder_roof + '/w1_slave'
device_folder_pool = glob.glob(base_dir + '28-030c979467d7')[0]
device_file_pool = device_folder_pool + '/w1_slave' 

# Default Parameters if database unavailable

defaultmaxpooltemp = 31
defaultstarthour = 9
defaultendhour = 17
defaultroofpooldelta = 6
defaultsleeptime = 300
defaultstartmonth = 10
defaultendmonth = 3

# Manual / Automatic Pump Switch

def manual_auto_switch_isr(channel):
    global pumpmanual
    pumpmanual = GPIO.input(18)
    if pumpmanual and not pumpstandby:
        GPIO.output(23, pumpOn)  # turn pump on
        lcdline4 = "Pump Manual"
        display_lcd(lcdline2, lcdline3, lcdline4)
    else:
        if not pumpstate == "On":  # Don't turn pump off if on automatically?
            lcdline4 = " "
            GPIO.output(23, pumpOff) # turn pump off
            display_lcd(lcdline2, lcdline3, lcdline4)
        
GPIO.add_event_detect(18, GPIO.RISING, callback = manual_auto_switch_isr, bouncetime=200)

# On / Standby Pump Switch

def on_standby_switch_isr(channel):
    global pumpstandby
    pumpstandby = GPIO.input(21)
    if pumpstandby and not pumpmanual:
        GPIO.output(23, pumpOff)  # turn pump off
        lcdline4 = "Pump Standby"
        display_lcd(lcdline2, lcdline3, lcdline4)
    else:
        lcdline4 = " "
        if pumpstate == "On":  # Turn pump back on if on automatically?
            GPIO.output(23, pumpOn) # turn pump on
        display_lcd(lcdline2, lcdline3, lcdline4)
        
GPIO.add_event_detect(21, GPIO.RISING, callback = on_standby_switch_isr, bouncetime=200)

# Connect to Database

def connect_database():
    try:
        global conn
        conn = mariadb.connect(
            user="username",
            password="password",
            host="localhost",
            port=3306,
            database="pooltemp"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        lcdline2 = "Error2"
        lcdline3 = "Error3"
        lcdline4 = "Db Connect Error"
        display_lcd(lcdline2, lcdline3, lcdline4)
        conn = "Error" 
        
# Retrieve configuration information from database

def get_config():
    # Get Cursor
    if conn != "Error": # Database Unavailable
        cursor = conn.cursor()
        try:  
            cursor.execute("SELECT dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth FROM pooltempconfig") 
            for dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth in cursor: 
                return dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth
    
        except mariadb.Error as e:
            print(f"Error accessing MariaDB Platform: {e}")
            # Return Default Parameters
            dmaxpooltemp = defaultmaxpooltemp
            dstarthour = defaultstarthour
            dendhour = defaultendhour
            droofpooldelta = defaultroofpooldelta
            dsleeptime = defaultsleeptime
            dstartmonth = defaultstartmonth
            dendmonth = defaultendmonth
            return dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth

    else:
        # Return Default Parameters
        dmaxpooltemp = defaultmaxpooltemp
        dstarthour = defaultstarthour
        dendhour = defaultendhour
        droofpooldelta = defaultroofpooldelta
        dsleeptime = defaultsleeptime
        dstartmonth = defaultstartmonth
        dendmonth = defaultendmonth
        return dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth
     
def save_temps():
# Get Cursor
    if conn != "Error":  # Database unavailable
        cursor = conn.cursor()
# Save temperatures   
        try:
            sql="INSERT INTO pool_temp (date, time, rooftemp, pooltemp, pumpstate) VALUES (?, ?, ?, ?, ?)"
            data = (date, time, roof, pool, pumpstate)
            cursor.execute(sql, data)
            conn.commit()
            conn.close()
        
        except mariadb.Error as e:
            print(f"Error accessing MariaDB Platform: {e}")

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
    
def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def display_lcd(lcdline2, lcdline3, lcdline4):
    lcd.text(datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S'), 1)
    lcd.text(lcdline2, 2)
    lcd.text(lcdline3, 3)
    lcd.text(lcdline4, 4)
    return

try:
    while True:
        connect_database()
        date = date.today()
        month = date.month
        time = datetime.datetime.now().time()        
        hour = int(time.strftime("%H"))
        dmaxpooltemp=get_config()
        maxpooltemp, starthour, endhour, roofpooldelta, sleeptime, startmonth, endmonth = dmaxpooltemp
        device_file = device_file_roof    # )get current
        roof = read_temp(device_file)     # )roof top temperature
        device_file = device_file_pool    # )get current
        pool = read_temp(device_file)     # )pool temperature
        lcdline2 = "Roof " + str(round(roof,1)) + "C"
        lcdline3 = "Pool " + str(round(pool,1)) + "C"
        display_lcd(lcdline2, lcdline3, lcdline4)
        if month > endmonth and month < startmonth:
            if not pumpmanual:
                GPIO.output(23, pumpOff)  #ensure pump off
                pumpstate = "Off"
                lcdline2 = lcdline2 + " Pump Off3"
                lcdline4 = "Not Summer"
            display_lcd(lcdline2, lcdline3, lcdline4)
            save_temps() #store timestamped temperatures in database
        else:
            if hour >= starthour and hour < endhour and not pumpmanual and not pumpstandby:  #is it after starttime or before endtime     
                if maxpooltemp > pool and roof > pool+roofpooldelta: #worth turning on pump?
                    GPIO.output(23, pumpOn)  #turn pump on
                    pumpstate = "On"
                    lcdline2 = lcdline2 + " Pump On"
                    if conn == "Error":
                        lcdline4 = "Database Error"
                    else:
                        lcdline4 = " "
                    display_lcd(lcdline2, lcdline3, lcdline4)
                    save_temps() #store timestamped temperatures in database
                else:
                    GPIO.output(23, pumpOff)  #turn pump off
                    pumpstate = "Off"
                    lcdline2 = lcdline2 + " Pump Off1"
                    if conn == "Error":
                        lcdline4 = "Database Error"
                    else:
                        lcdline4 = " "
                    display_lcd(lcdline2, lcdline3, lcdline4)
                    save_temps() #store timestamped temperatures in database
            else:
                if not pumpmanual and not pumpstandby:
                    GPIO.output(23, pumpOff)  #turn pump off
                    pumpstate = "Off"
                    lcdline2 = lcdline2 + " Pump Off2"
                    if conn == "Error":
                        lcdline4 = "Database Error"
                    else:
                        lcdline4 = " "            
                    display_lcd(lcdline2, lcdline3, lcdline4)
                    save_temps() #store timestamped temperatures in database
        sleep(sleeptime)

except KeyboardInterrupt:
    GPIO.cleanup()
    lcd.clear()
finally:
    GPIO.cleanup()
    lcd.clear()
