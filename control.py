#!/usr/bin/python3
##
import RPi.GPIO as GPIO
import time
import sys
import ast
from pathlib import Path as P

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setwarnings(False)
 
PIN = 17
GPIO.setup(PIN, GPIO.OUT) # GPIO Assign mode 
pwm = GPIO.PWM(PIN, 3000)

f = str(P(__file__).parent.joinpath('commands.txt'))
default = {
    'com':'',
    'on':0.25,
    'off':1.75,
    'rep':600,
    'bri':100
}
P(f).write_text(repr(default))

com = default['com']
on = default['on']
off = default['off']
rep = default['rep']
bri = default['bri']
prev = P(f).stat().st_mtime
stopped = False

cc = 0
while True:
    pause = False
    change = True
    starttime = time.time()
    looptime = time.time()
    status = False
    pwm.start(0)
    prevtime = 0
    if P(f).stat().st_mtime > prev:
        args = ast.literal_eval(P(f).read_text()) 
        com = args['com']
        on = args['on']
        off = args['off']
        rep = args['rep']
        bri = args['bri']
        prev = P(f).stat().st_mtime
        if not com == 'stop':
            stopped = False
    if not stopped:
        P(__file__).parent.joinpath('progress.txt').write_text(f"Progress 0%")
        while time.time() < starttime + rep:
            #    while cc < 1:
            if P(f).stat().st_mtime > prev:
                args = ast.literal_eval(P(f).read_text()) 
                com = args['com']
                bri = args['bri']
                prev = P(f).stat().st_mtime
            if com == 'set':
                args = ast.literal_eval(P(f).read_text()) 
                com = args['com']
                on = args['on']
                off = args['off']
                rep = args['rep']
                bri = args['bri']
                args['com'] = ''
                P(f).write_text(repr(args))
                break
            if com == '':
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
                    if status:
                        time.sleep(on / 1000)
                        if change:
                            status = False
                            b = 0
                            looptime = time.time() + off
                    elif not status:
                        time.sleep(off / 1000)
                        if change:
                            status = True
                            b = bri
                            looptime = time.time() + on
                    #GPIO.output(PIN, status)
                    pwm.ChangeDutyCycle(b)
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
                ll = 0
                while ll < 5:
                    for bb in range(0, 101, 2):
                        pwm.ChangeDutyCycle(bb)
                        time.sleep(0.005)
                    for bb in range(95, 0, -2):
                        pwm.ChangeDutyCycle(bb)
                        time.sleep(0.005)
                    ll += 1
        if stopped:
            for bb in range(100, 0, -2):
                pwm.ChangeDutyCycle(bb)
                time.sleep(0.05)
        else:
            ll = 0
            while ll < 2:
                for bb in range(0, 101, 2):
                    pwm.ChangeDutyCycle(bb)
                    time.sleep(0.005)
                for bb in range(95, 0, -2):
                    pwm.ChangeDutyCycle(bb)
                    time.sleep(0.005)
                ll += 1
            stopped = True
    
    if com == 'stop':
        time.sleep(0.05)
