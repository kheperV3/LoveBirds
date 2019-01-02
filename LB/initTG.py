from flask import Flask, render_template, redirect, url_for, request, make_response
import datetime
import os

app = Flask(__name__)


@app.route('/',methods = ['POST', 'GET'])
def index():

    now = datetime.datetime.now()
    timeString = now.strftime("%H:%M:%S      %d/%m/%Y")
    template = {
        'title' : 'LOVE BIRDS',
        'time' : timeString
        }
    if request.method == 'POST':
        peer = request.form['peer']
        if len(peer) > 0:
            f = open('/boot/peer', 'w')
            f.write(peer)
            f.close()
            #os.system('chown pi /home/pi/peer')
            #os.system('chgrp pi /home/pi/peer')
        phone = request.form['phone']
        if len(phone) > 0:
            f = open('/home/pi/phone', 'w')
            f.write(phone)
            f.close()
            os.system('chown pi /home/pi/phone')
            os.system('chgrp pi /home/pi/phone')
        key = request.form['key']
        if len(key) > 0:
            f = open('/home/pi/key', 'w')
            f.write(key)
            f.close()
            os.system('chown pi /home/pi/key')
            os.system('chgrp pi /home/pi/key')

    return  render_template('index.html', **template)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

