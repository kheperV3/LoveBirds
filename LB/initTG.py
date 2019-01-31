from flask import Flask, render_template, redirect, url_for, request, make_response
import datetime
import os

app = Flask(__name__)


@app.route('/',methods = ['POST', 'GET'])
def index():

    now = datetime.datetime.now()
    timeString = now.strftime("%H:%M:%S      %d/%m/%Y")
    
    txt = open('/boot/PEER.txt', 'r')
    currentPeer = txt.read()
    txt.close()

    txt = open('/home/pi/phone', 'r')
    currentPhone = txt.read()
    txt.close()



    if request.method == 'POST':
        peer = request.form['peer']
        if len(peer) > 0:
            f = open('/boot/PEER.txt', 'w')
            f.write(peer)
            f.close()
            os.system('sudo reboot&')
            #os.system('chgrp pi /home/pi/peer')
        phone = request.form['phone']
        if len(phone) > 0:
            f = open('/home/pi/phone', 'w')
            f.write(phone)
            currentPhone = phone
            f.close()
            os.system('chown pi /home/pi/phone')
            os.system('chgrp pi /home/pi/phone')
            os.system('sudo reboot&')
        key = request.form['key']
        if len(key) > 0:
            f = open('/home/pi/key', 'w')
            f.write(key)
            f.close()
            os.system('chown pi /home/pi/key')
            os.system('chgrp pi /home/pi/key')
        password = request.form['password']
        if len(password) > 0:
            f = open('/home/pi/password', 'w')
            f.write(password)
            f.close()
            os.system('chown pi /home/pi/password')
            os.system('chgrp pi /home/pi/password')

    template = {
        'title' : 'LOVE BIRDS',
        'time' : timeString,
        'currentPeer' : currentPeer,
        'currentPhone' : currentPhone
        }


    return  render_template('index.html', **template)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

