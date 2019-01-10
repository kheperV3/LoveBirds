# LOVE BIRDS

## Send and receive voice messages using Raspberry PI Zero and Telegram


### What is Love (birds)?

It’s a standalone device to receive send voice messages with one person: lover, family or friend. Open the box, push on the button while you talk, release to send. Your correspondent will receive the voice message on his Telegram phone app or on his own LoveBirds box with a nice motor move and bird song.

See the video here: https://www.youtube.com/watch?v=enLJgY6dZ9U



This is the method to install from scratch the Love Birds projects. **If you want an easier installation method please follow the intructable here to just burn the prebuilt SD card:**

https://www.instructables.com/id/Love-Birds-a-Box-to-Send-and-Receive-Telegram-Audi/
or here https://www.raspiaudio.com/lovebirds/


### Ok so you want to go the hard way and rebuild it from scratch:

 
#### Architecture:
  
    initWiFi ⇒ initialize wifi access takes the file on /boot/WIFI.txt (easily accessible by just editing the file with a windows computer and SD car reader) and rename it wpa_supplicant.conf and copy it /etc/wpa_supplicant/wpa_supplicant.conf
    
    initTG.py ⇒ initialize the telegram connection, to send messages as the user. configuration is done using a web page managed by Flask that basicaly asks the user to give his Telegram phone number, the confirmation received by SMS, and the name of te correspondent (who you want to talk to).It is copying the PHONE and PEER.txt in some file used later by valentin.py
    
      . PEER.txt the input format is @JohnBlack
      
      . PHONE international format +33777792516
      
      . Sms configiration file 12345
      
      valentin.py ⇒ the application itself
      

#### Installation steps
  -Start from a Raspbian Stretch Lite, and burn it on a SD card https://downloads.raspberrypi.org/raspbian_lite_latest

  ##### Required packages:

      . telethon
      
          sudo apt-get install python3-pip
          
          sudo pip3 install telethon
          

      . sox
      
          sudo apt-get install sox
          
      . vlc
      
          sudo apt-get vlc
          
       . GPIO
       
          sudo apt-get install python3-gpiozero
          
          sudo apt-get install python-rpi.gpio python3-rpi.gpio
          
        Flask
        
          sudo pip3 install flask
          


   ##### If you use the MIC+ sound card install it, otherwise skip this section. MIC+ it's a cool sound card has it has all in one 2 speakers, microphone and a button led. https://www.raspiaudio.com/raspiaudio-aiy
   
        sudo wget -O mic mic.raspiaudio.com
        
        sudo bash mic
        
      -Say yes for the reboot
      
      -On the next reboot you  have to run the test to finish the installation (it is an ALSA oddness):
      
        sudo wget -O test test.raspiaudio.com
        
        sudo bash test
        
      Push the onboard button, you should hear "Front Left" "front Right" then the recorded sequence by the microphone.
      


  ##### Start the programs on boot
  Copy the content of this GIT of the directory /LB in /home/pi/LB
  sudo cp /home/pi/LB/rc.local  /etc
  boot the sytem and start a browser from any computer of your local network to complete the configuration of Telegram (see the instructable from that point.)
  






