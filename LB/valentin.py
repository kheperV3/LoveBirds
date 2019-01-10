#credit to Louis Ros


#!/usr/bin/python3.5
import asyncio
import time
import os
import sys
import signal
from telethon import TelegramClient, events, sync
from telethon.tl.types import InputMessagesFilterVoice
import RPi.GPIO as GPIO
from gpiozero import Servo
from time import sleep


"""
initialisation of GPIOs
"""
global recLED      #led recording (mic+)
global recBUT      #button recording (mic+)
global playLED     #led you have a voicemail
global p


global toPlay      # number of voicemail waiting
global recD        # duration of recording (in half second)
global playOK      # autorisation to play messages (boolean)
global playOKD     # timeout(en 1/2 secondes) de l'autorisation
global motorON     # motor command
global previousMotorON #was the motor on before?
global heartBeatLed #heartbeat effect on led
global motor

heartBeatLed = False
previousMotorON = False
motorON = False
playOK = False
recD = 0
playOKD = 0

toPlay = -1
playLED = 22
recLED = 25
recBUT = 23
motor = 17

"""
initialisation of GPIO leds and switch and motor
"""
GPIO.setmode(GPIO.BCM)
GPIO.setup(recLED, GPIO.OUT)
GPIO.setup(recBUT, GPIO.IN)
GPIO.setup(playLED, GPIO.OUT)
GPIO.setup(motor, GPIO.OUT)
GPIO.output(recLED, GPIO.LOW)


async def timeC():
    """
    time management : duration of recording and timeout for autorization to play
    """
    global playOK
    global playOKD
    global recD
    global motorON

    while True :
        await asyncio.sleep(0.5)
        recD = recD + 1
        if playOK == True:
            playOKD = playOKD - 1
            if playOKD <= 0:
                playOK = False



async def recTG():
    """
    Send a message 'voice'
    initialisation of gpio led and button
    when button is pushed: recording in a separate process
    that is killed when the button is released
    conversion to .oga by sox
    """
    global recD
    global playOK
    global playOKD
    delay = 0.2 
    while True:    
        await asyncio.sleep(delay)
        if GPIO.input(recBUT) == GPIO.LOW:
            heartBeatLed = False
            p.ChangeDutyCycle(100) #turns ON the REC LED
            recD = 0
            pid = os.fork()
            if pid == 0 :
                os.execl('/usr/bin/arecord','arecord','--rate=44000','/home/pi/rec.wav','')
            else:
                while GPIO.input(recBUT) == GPIO.LOW :
                    await asyncio.sleep(delay)
                os.kill(pid, signal.SIGKILL)
                heartBeatLed = False
                #GPIO.output(recLED, GPIO.LOW)
                p.ChangeDutyCycle(0) #turns OFF the REC LED
                playOK = True
                playOKD = 30
                if recD > 1:
                    os.system('sudo killall sox')
                    os.system('/usr/bin/sox /home/pi/rec.wav /home/pi/rec.ogg')
                    os.rename('/home/pi/rec.ogg', '/home/pi/rec.oga')
                    await client.send_file(peer, '/home/pi/rec.oga',voice_note=True)
        else:
            #heartBeatLed = False
            #GPIO.output(recLED, GPIO.LOW)
            p.ChangeDutyCycle(0)

#motor uses global to turn ON the motor
async def motor():
	global motorON
	global motor
	global previousMotorON
	# Adjust the pulse values to set rotation range
	min_pulse = 0.000544    # Library default = 1/1000
	max_pulse = 0.0024              # Library default = 2/1000
	# Initial servo position
	pos =  1
	test = 0
	servo = Servo(17, pos, min_pulse, max_pulse, 20/1000, None)
	

	while True:
		await asyncio.sleep(0.2)
		if motorON == True:
			pos=pos*(-1)
			servo.value=pos
			await asyncio.sleep(2)
		else :
                        #put back in original position
                        servo.value=0
                        #detach the motor to avoid glitches and save energy
                        servo.detach()
                        previousMotorON = False

#this is the les that mimic heartbeat when you have a voicemail waiting
async def heartBeat():
	global heartBeatLed
	global p


	p = GPIO.PWM(recLED, 500)     # set Frequece to 500Hz
	p.start(100)                     # Start PWM output, Duty Cycle = 0
	while True:
		if heartBeatLed == True :
			for dc in range(0, 20, 2):   # Increase duty cycle: 0~100
				p.ChangeDutyCycle(dc)
				await asyncio.sleep(0.01)
			for dc in range(20, -1, -2): # Decrease duty cycle: 100~0
				p.ChangeDutyCycle(dc)
				await asyncio.sleep(0.005)
			time.sleep(0.05)
	
			for dc in range(0, 101, 2):   # Increase duty cycle: 0~100
				p.ChangeDutyCycle(dc)     # Change duty cycle
				await asyncio.sleep(0.01)
			for dc in range(100, -1, -2): # Decrease duty cycle: 100~0
				p.ChangeDutyCycle(dc)
				await asyncio.sleep(0.01)

			await asyncio.sleep(0.06)
	
			for dc in range(0,8, 2):   # Increase duty cycle: 0~100
				p.ChangeDutyCycle(dc)     # Change duty cycle
				await asyncio.sleep(0.01)
			for dc in range(7, -1, -1): # Decrease duty cycle: 100~0
				p.ChangeDutyCycle(dc)
				await asyncio.sleep(0.01)
			await asyncio.sleep(1)
			
		else :
                        await asyncio.sleep(0.1)



async def playTG():
    """
    when authorized to play (playOK == True)
    play one or several messages waiting (file .ogg) playLED on
    message playing => playing
    last message waiting => toPlay
    """
    global toPlay
    global playOK
    global motorON
    global heartBeatLed
    global servo

    playing = 0
    while True:
        if toPlay >= 0:
            GPIO.output(playLED, GPIO.HIGH)
            motorON = True
            heartBeatLed = True
            
        else:
            GPIO.output(playLED, GPIO.LOW)
            motorON = False
            heartBeatLed = False

            
        if (toPlay >= 0) and (playOK == True):
            while playing <= toPlay:
                name = '/home/pi/play' + str(playing) + '.ogg'
                os.system('sudo killall vlc')

                pid = os.fork()
                if pid == 0 :
                    os.execl('/usr/bin/cvlc', 'cvlc', name,  '--play-and-exit')
                    #os.execl('/usr/bin/cvlc', 'cvlc',  name, ' vlc://quit')

                os.wait()         
                playing = playing + 1
                if playing <= toPlay :
                    await asyncio.sleep(1)
            playing = 0
            toPlay = -1  
            playOk = True
            playOKD = 30     
        await asyncio.sleep(0.2)




"""
initialization of the application and user for telegram
init of the name of the correspondant with the file /boot/PEER.txt
declaration of the handler for the messages arrival
filtering of message coming from the correspondant
download of file .oga renamed .ogg

"""
GPIO.output(playLED, GPIO.HIGH)
motorON=True
api_id = 592944
api_hash = 'ae06a0f0c3846d9d4e4a7065bede9407'
client =  TelegramClient('session_name', api_id, api_hash)
asyncio.sleep(2)
client.connect()
if not  client.is_user_authorized():
    while os.path.exists('/home/pi/phone') == False:
        pass
    f = open('/home/pi/phone', 'r')
    phone = f.read()
    f.close()
    os.remove('/home/pi/phone')
    print(phone)

    asyncio.sleep(2)
    client.send_code_request(phone,force_sms=True)

    while os.path.exists('/home/pi/key') == False:
        pass
    f = open('/home/pi/key', 'r')
    key = f.read()
    f.close()
    print (key)
    os.remove('/home/pi/key')
    asyncio.sleep(2)
    me = client.sign_in(phone=phone, code=key)
GPIO.output(playLED, GPIO.LOW)        
motorON=False

p = open('/boot/PEER.txt','r')
peer = p.readline() 
if peer[-1] == '\n':
    peer = peer[0:-1]
#print(peer)
#print(len(peer))
@client.on(events.NewMessage)
async def receiveTG(event):
    global toPlay
    #print(event.stringify())
    fromName = '@' + event.sender.username
    
    #only plays messages sent by your correpondant, if you want to play messages from everybody comment next line and uncomment the next next line
    if (event.media.document.mime_type  == 'audio/ogg') and (peer == fromName) :
    #if (event.media.document.mime_type == 'audio/ogg'): 
            ad = await client.download_media(event.media)
            #print('ok')
            toPlay =   toPlay + 1
            #print(toPlay)
            if toPlay == 0:
                #os.system('/usr/bin/cvlc --play-and-exit /home/pi/LB/lovebird.wav')
                os.system('/usr/bin/cvlc --play-and-exit /home/pi/LB/lovebird.wav')
            name = '/home/pi/play' + str(toPlay) +  '.ogg'
            #print(name)
            os.rename(ad,name)
            await asyncio.sleep(0.2)
            #os.system('/usr/bin/cvlc --play-and-exit ' +  name)
           
"""
Main sequence (handler receiveTG), playTG, timeC, recTG, motor et heartBeat are excuted in parallel

"""
#os.system('/usr/bin/cvlc /home/pi/LB/lovebird.wav vlc://quit')
os.system('/usr/bin/cvlc --play-and-exit /home/pi/LB/lovebird.wav')

loop = asyncio.get_event_loop()
loop.create_task(recTG())
loop.create_task(playTG())
loop.create_task(timeC())
loop.create_task(motor())
loop.create_task(heartBeat())
loop.run_forever()
client.run_until_disconnected()

