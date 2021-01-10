#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import sys
import ast
from pathlib import Path as P

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setwarnings(False)
 
PIN = 17
GPIO.setup(PIN, GPIO.OUT) # GPIO Assign mode 

f = str(P(__file__).parent.joinpath('commands.txt'))
default = {
    'com':'',
    'on':0.25,
    'off':1.75,
    'rep':600
}
P(f).write_text(repr(default))

com = default['com']
on = default['on']
off = default['off']
rep = default['rep']
prev = P(f).stat().st_mtime
stopped = False

cc = 0
while True:
    pause = False
    change = True
    starttime = time.time()
    looptime = time.time()
    status = GPIO.LOW
    prevtime = 0
    if P(f).stat().st_mtime > prev:
        args = ast.literal_eval(P(f).read_text()) 
        com = args['com']
        on = args['on']
        off = args['off']
        rep = args['rep']
        prev = P(f).stat().st_mtime
        if not com == 'stop':
            stopped = False
    if not stopped:
        while time.time() < starttime + rep:
            #    while cc < 1:
            if P(f).stat().st_mtime > prev:
                args = ast.literal_eval(P(f).read_text()) 
                com = args['com']
                prev = P(f).stat().st_mtime
            if com == 'set':
                args = ast.literal_eval(P(f).read_text()) 
                com = args['com']
                on = args['on']
                off = args['off']
                rep = args['rep']
                P(f).write_text(repr({'com':'','on':on,'off':off,'rep':rep}))
                break
            elif com == '':
                if pause:
                    starttime += time.time() - pausestart
                    looptime += time.time() - pausestart
                    pause = False
                    change = False
                if time.time() > looptime:
                    if rep > 600:
                        if int(time.time() - starttime - prevtime) % (rep // 200) == 0 and int(time.time() - starttime - prevtime) > 0:
                            P(__file__).parent.joinpath('progress.txt').write_text(f"Progress { (time.time() - starttime) / rep * 100 :.1f}%")
                            prevtime = int(time.time() - starttime)
                    if P(f).stat().st_mtime > prev:
                        args = ast.literal_eval(P(f).read_text()) 
                        com = args['com']
                        prev = P(f).stat().st_mtime
                    if status == GPIO.HIGH:
                        time.sleep(on / 1000)
                        if change:
                            status = GPIO.LOW
                            looptime = time.time() + off
                    elif status == GPIO.LOW:
                        time.sleep(off / 1000)
                        if change:
                            status = GPIO.HIGH
                            looptime = time.time() + on
                    GPIO.output(PIN, status)
                    cc += 1
                if not change:
                    change = True
            elif com == 'pause':
                if pause == False:
                    pausestart = time.time()
                    pause = True
                time.sleep((on + off) / 1000 )
                pass
            elif com == 'stop':
                stopped = True
                break
            else:
                GPIO.output(PIN, GPIO.LOW) 
                time.sleep(0.1)
                GPIO.output(PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(PIN, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(PIN, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(PIN, GPIO.HIGH)
                time.sleep(0.5)
    
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.25)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.25)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(0.25)
        GPIO.output(PIN, GPIO.LOW)
        stopped = True
    
    if com == 'stop':
        time.sleep(0.05)
