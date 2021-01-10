import time
import sys
import os
import warnings
import subprocess

from dearpygui.core import *
from dearpygui.simple import *

"""
To being pulsing function on RPi, select 'Start' from menu bar
Enter times (in seconds, minutes, or hours) in the entry windows to the left\n" + 
'On' is length that LED is on
'Off' is length that LED is off
'For' is total length of time to cycle
Make sure you choose your time unit using the selection on the right!
'Pause' will pause cycling, 'Stop' will break execution loop
Use 'Stop' if you want to change parameters (and click 'Set times' again!)
"""

def set_times(sender, data):
    targstrings = [('on', 'On'), ('off', 'Off'), ('rep', 'For')]
    timedict = {'on':(' s', 1), 'off':(' s', 1), 'rep':(' s', 1)}
    printdict = {'on':'not set', 'off':'not set', 'rep':'not set'}
    multdict = {'s':1, 'min':60, 'hr':3600}
    for i, o in targstrings:
        try:
            add_data(i, abs(float(get_value(o))))
            set_value(o, get_data(i))
            timedict[i] = ([' '+ii.split("##")[0] for ii in get_all_items() if (ii.endswith(f"##{i}") and get_value(ii) is True)][0], multdict[[ii.split("##")[0] for ii in get_all_items() if (ii.endswith(f"##{i}") and get_value(ii) is True)][0]])
            if float(get_value(o)) == int(float(get_value(o))):
                printdict[i] = int(float(get_value(o)))
            else:
                printdict[i] = get_value(o)
        except ValueError:
            add_data(i, 'not set')
            set_value(o, "Error")
            timedict[i] = ('', 0)
        except IndexError:
            add_data(i, abs(float(get_value(o))))
            set_value(o, get_data(i))
            timedict[i] = (' NO UNIT', 'Error string instead of float')
            if float(get_value(o)) == int(float(get_value(o))):
                printdict[i] = int(float(get_value(o)))
            else:
                printdict[i] = get_value(o)
    add_data('times', timedict)
    add_data('timestr', f"On: {printdict['on']}{timedict['on'][0]}, Off: {printdict['off']}{timedict['off'][0]}, For: {printdict['rep']}{timedict['rep'][0]}")
    on = get_data('on')*get_data('times')['on'][1]
    off = get_data('off')*get_data('times')['off'][1]
    rep = get_data('rep')*get_data('times')['rep'][1]
    set_value("settings", get_data('timestr'))


def loop(sender, data):
    try:
        set_value("status", f"Sending times to RPi")
        time.sleep(3.5)
        add_data('cancel', False)
        add_data('pause', False)
        count = 0
        starttime = time.time()
        endtime = starttime + get_data('rep')*get_data('times')['rep'][1]
        add_data('running', True)
        pausehold = 0
        sleeptime = 0
        add_data('which', 'on')
        set_value("status", f"Running: LED on")
        set_value("settings", get_data('timestr'))
        on = get_data('on')*get_data('times')['on'][1]
        off = get_data('off')*get_data('times')['off'][1]
        rep = get_data('rep')*get_data('times')['rep'][1]
        targtime = starttime + on
        while time.time() <= endtime:
            if get_data('cancel'):
                set_value("status", "Cancelled")
                add_data('pause', False)
                break
            if get_data('pause'):
                pausestart = time.time()
                while True:
                    set_value("status", "Paused")
                    if get_data('cancel'):
                        break
                    if not get_data('pause'):
                        pausehold += time.time() - pausestart
                        endtime += time.time() - pausestart
                        targtime += time.time() - pausestart
                        break
            if time.time() > targtime:
                if get_data('which') == 'on':
                    add_data('which', 'off')
                    targtime += get_data('off')*get_data('times')['off'][1]
                    set_value("status", f"Running: LED off")
                    sleeptime = get_data('off')*get_data('times')['off'][1] / 100
                elif get_data('which') == 'off':
                    add_data('which', 'on')
                    targtime += get_data('on')*get_data('times')['on'][1]
                    set_value("status", f"Running: LED on")
                    sleeptime = get_data('on')*get_data('times')['on'][1] / 100
            set_value("progbar", (time.time() - starttime - pausehold) / (endtime - starttime - pausehold))
            time.sleep(sleeptime)
        if not get_data('cancel'):
            set_value("progbar", 1)
            set_value("status", "Complete")
        add_data('running', False)
    except TypeError:
        set_value("settings", "Times not set")
        set_value("status", "Inactive")


def cancel_prog(sender, data):
    add_data('cancel', True)
    subprocess.Popen(["ssh", "pi@169.231.182.39",f"python3 ~/Documents/code/python/writecontrol.py stop 0 0 0 &"])
    if get_data('pause'):
        add_data('pause', False)
        configure_item("Pause", label="Pause")


def pause_prog(sender, data):
    if get_data('pause'):
        add_data('pause', False)
        configure_item("Pause", label="Pause")
        on = get_data('on')*get_data('times')['on'][1]
        off = get_data('off')*get_data('times')['off'][1]
        rep = get_data('rep')*get_data('times')['rep'][1]
        subprocess.Popen(["ssh", "pi@169.231.182.39",f"python3 ~/Documents/code/python/writecontrol.py '' {on} {off} {rep}"])
    elif get_data('running'):
        on = get_data('on')*get_data('times')['on'][1]
        off = get_data('off')*get_data('times')['off'][1]
        rep = get_data('rep')*get_data('times')['rep'][1]
        subprocess.Popen(["ssh", "pi@169.231.182.39",f"python3 ~/Documents/code/python/writecontrol.py pause {on} {off} {rep}"])
        add_data('pause', True)
        configure_item("Pause", label="Resume")


def start_cbk(sender, data):
    if not get_data('running'):
        on = get_data('on')*get_data('times')['on'][1]
        off = get_data('off')*get_data('times')['off'][1]
        rep = get_data('rep')*get_data('times')['rep'][1]
        subprocess.Popen(["ssh","pi@169.231.182.39",f"python3 ~/Documents/code/python/writecontrol.py set {on} {off} {rep}"])
        set_value("progbar", 0)
        run_async_function(loop, data)
    else:
        set_value("status", "ALREADY RUNNING")


def mkfalse(sender, data):
    [set_value(ii, False) for ii in get_all_items() if "##" in ii and sender.split("##")[1] in ii and sender != ii]


def startPi(sender, data):
    subprocess.run(["ssh","pi@169.231.182.39",'pkill -f control.py'])
    if sender == 'connect':
        subprocess.Popen(["ssh","pi@169.231.182.39",'python3 ~/Documents/code/python/control.py'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def create_menu():
    with menu_bar("Main menu bar", parent="Main"):
        with menu("LED control"):
            add_menu_item('connect', label="Connect", callback=startPi)
            add_menu_item('disconnect', label="Disconnect", callback=startPi)
        add_menu_item('help', label="Help", callback=showHelp)

def showHelp(sender,data):
    log_info("\n-To begin, select 'Connect' from menu bar\n-Enter times (in seconds, minutes, or hours)\nin the entry boxes to the left\n-'On'/'Off'/'For' is time that LED is on/off/looped\n-Make sure you choose unit!\n-'Pause' will pause cycling, 'Stop' will end it.\n-Must be stopped to change settings\n-3 0.25s pulses mean sequence is done or\nnew settings have been applied.\n-2 long, 2 short means there's an error.")
    show_logger()


set_global_font_scale(1.2)
set_main_window_size(375, 225)
set_main_window_title("RPi-controlled LED GUI")
with window("Main"):
    create_menu()
    add_button("Set times", callback=set_times, height=30, width=80)
    set_item_color("Set times", mvGuiCol_Button, [0, 0, 150, 255])
    add_same_line(spacing=7)
    add_button("Start", callback=start_cbk, height=30, width=80)
    set_item_color("Start", mvGuiCol_Button, [0, 150, 0, 255])
    add_same_line(spacing=7)
    add_button("Pause", callback=pause_prog, label="Pause", height=30, width=80)
    set_item_color("Pause", mvGuiCol_Button, [200, 200, 0, 255])
    add_same_line(spacing=7)
    add_button("Stop", callback=cancel_prog, height=30, width=80)
    set_item_color("Stop", mvGuiCol_Button, [255, 0, 0, 255])

    add_input_text("On", label="On", width=80, hint="On time")
    add_same_line(spacing=16)
    add_checkbox('s##on', default_value=True, callback=mkfalse, label="sec")
    add_same_line(spacing=10)
    add_checkbox('min##on', default_value=False, callback=mkfalse, label="min")
    add_same_line(spacing=10)
    add_checkbox('hr##on', default_value=False, callback=mkfalse, label="hour")
    add_input_text("Off", label="Off", width=80, hint="Off time")
    add_same_line(spacing=7)
    add_checkbox('s##off', default_value=True, callback=mkfalse, label="sec")
    add_same_line(spacing=10)
    add_checkbox('min##off', default_value=False, callback=mkfalse, label="min")
    add_same_line(spacing=10)
    add_checkbox('hr##off', default_value=False, callback=mkfalse, label="hour")
    add_input_text("For", label="For", width=80, hint="How long")
    add_same_line(spacing=7)
    add_checkbox('s##rep', default_value=False, callback=mkfalse, label="sec")
    add_same_line(spacing=10)
    add_checkbox('min##rep', default_value=True, callback=mkfalse, label="min")
    add_same_line(spacing=10)
    add_checkbox('hr##rep', default_value=False, callback=mkfalse, label="hour")
    add_label_text("settings", default_value=f"On: not set, Off: not set, For: not set")
    add_label_text("status", default_value=f"Inactive")
    add_progress_bar("progbar", overlay="Progress", width=341) 

    add_data('running', False)
    add_data('pause', False)

start_dearpygui(primary_window="Main")
