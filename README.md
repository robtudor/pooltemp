# pooltemp
This project control 240V mains power so appropriate caution should be employed.
Code for a Raspberry Pi to control a pool solar heating pump
A Raspberry Pi Zero W controls a water pump via a relay.
The Pi regularly, (the interval is configurable) interrogates two DS18B20 waterproof temperature sensors, 
one is located on the roof attached to the solar heating outlet pipe and the other is attached
to the inlet pipe of the pump at ground level. The sensors are connected via Cat 5 cable, the roof cable is about
15 metres long and the other is about 2 metres.
If the difference in temperature is deemed to be sufficient, the pump is turned on, otherwise it is turned off.
At the sensor interrogation interval, the outlet and inlet temperatures, together with the date and time and the
status of the pump, either on or off, are recoded in a MariaDB database, this information
is also displayed on a 4 line LCD located on the unit itself.
There are two toggle switches on the unit, one is to switch between standby (pump off)/ and On and
the other is to manually switch the pump on.
The automatic switching on of the pump is determined by the time of day, the date, the maximum outlet temperature,
and the temperature difference between the two sensors. All of these parameters and the interrogation interval 
are stored in the Maria database and are configurable. Default parameters are supplied if the database is unavailable.
A web accessible python script is used to access the database and provide current sensor temperatures (as at the last interrogation),
maximum output temperatures for the day and minimum output temperatures for the day.
A crontab script prunes the database tables every month.
