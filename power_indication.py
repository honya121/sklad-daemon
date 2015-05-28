import os as os
import RPi.GPIO as GPIO
import time as time
import io

class PowerIndication:
	def __init__(self):
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)	#inicializace pinu pro power_tlacitko
			GPIO.setup(17, GPIO.OUT)				#inicializace pinu pro power_led
			GPIO.setup(18, GPIO.OUT)				#inicializace pinu pro eth0_link_led
			GPIO.output(17, GPIO.HIGH)				#rozsviceni power_led, zhasne, az se RasPi vypne
			GPIO.output(18, GPIO.LOW)
			self.flog = file("log.out", "w");
			self.frx = io.open("/sys/class/net/eth0/statistics/rx_bytes", "r");
			self.ftx = io.open("/sys/class/net/eth0/statistics/tx_bytes", "r");
			self.rx = 0;
			self.tx = 0;
			self.oldrx = 0;
			self.oldtx = 0;
			self.eth_led_state = True;
			self.power_button_hold = False;
	def loop(self):
			if GPIO.input(4) == GPIO.LOW:
				return True
			self.oldrx = rx;
			self.oldtx = tx;
			self.frx.seek(0);
			self.ftx.seek(0);
			self.rx = int(frx.read().strip());
			self.tx = int(ftx.read().strip());
			os.system("ethtool eth0 | grep 'Link detected:' > tmp.out");
			output = open("tmp.out", "r").read().strip();
			if(output == "Link detected: yes"):
				GPIO.output(18, GPIO.HIGH);
				self.flog.write(output);
				if(self.rx != self.oldrx or self.tx != self.oldtx):
					if(self.eth_led_state):
						GPIO.output(18, GPIO.HIGH);
						self.eth_led_state = False;
					else:
						GPIO.output(18, GPIO.LOW);
						self.eth_led_state = True;
			else:
				GPIO.output(18, GPIO.OUT);
			if GPIO.input(4) != GPIO.HIGH:
				self.power_button_hold = True;
			time.sleep(0.125)
			if GPIO.input(4) != GPIO.HIGH and self.power_button_hold == True:
				break;
			self.power_button_hold = False;
	def powerOff(self):
		GPIO.output(17, GPIO.LOW);
		time.sleep(0.25);
		GPIO.output(17, GPIO.HIGH);
		time.sleep(0.25);
		GPIO.output(17, GPIO.LOW);
		time.sleep(0.25);
		GPIO.output(17, GPIO.HIGH);
		time.sleep(0.25);
		GPIO.output(17, GPIO.LOW);
		time.sleep(0.25);
		GPIO.output(17, GPIO.HIGH);
		time.sleep(0.25);
		GPIO.output(17, GPIO.LOW);
		time.sleep(0.25);
		GPIO.output(17, GPIO.HIGH);
		os.system("poweroff")					#vypnuti RasPi
		
