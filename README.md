# pooltemp
This project controls 240V mains power so appropriate caution should be employed.<br>
Code for a Raspberry Pi to control a pool solar heating pump<br>
A Raspberry Pi Zero W controls a water pump via a relay.<br>
The Pi regularly, (the interval is configurable) interrogates two DS18B20 waterproof temperature sensors, 
one is located on the roof attached to the solar heating outlet pipe and the other is attached
to the inlet pipe of the pump at ground level. The sensors are connected via Cat 5 cable, the roof cable is about
15 metres long and the other is about 2 metres.<br>
If the difference in temperature is deemed to be sufficient, the pump is turned on, otherwise it is turned off.<br>
At the sensor interrogation interval, the outlet and inlet temperatures, together with the date and time and the
status of the pump, either on or off, are recorded in a MariaDB database, this information
is also displayed on a 4 line LCD located on the unit itself.<br>
There are two toggle switches on the unit, one is to switch between standby (pump off)/ and On and
the other is to manually switch the pump on.<br>
The automatic switching on of the pump is determined by the time of day, the date, the maximum outlet temperature,
and the temperature difference between the two sensors.<br> All of these parameters and the interrogation interval 
are stored in the MariaDB database and are configurable. Default parameters are supplied if the database is unavailable.<br>
A web accessible python script is used to access the database and provide current sensor temperatures (as at the last interrogation),
maximum output temperatures for the day and minimum output temperatures for the day, additionally the pump parameters are configurable
via the web.<br>
A crontab script prunes the database tables every month.
Wifi is monitored every 20 seconds and is restarted if necessary.
