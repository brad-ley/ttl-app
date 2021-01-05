import time
import serial
import glob
import sys
import os
import pyautogui
import warnings

from dearpygui.core import *
from dearpygui.simple import *

def set_times(sender, data):
    if not get_data('running'):
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
        set_value("settings", f"On: {printdict['on']}{timedict['on'][0]}, Off: {printdict['off']}{timedict['off'][0]}, For: {printdict['rep']}{timedict['rep'][0]}")
    else:
        set_value('status', "CURRENTLY RUNNING")


def loop(sender, data):
    try:
        port = get_data('port')
        add_data('cancel', False)
        add_data('pause', False)
        count = 0
        starttime = time.time()
        endtime = starttime + get_data('rep')*get_data('times')['rep'][1]
        add_data('running', True)
        pausehold = 0
        sleeptime = 0
        # ser = serial.Serial(get_data('com'))
        ser = get_data('ser')
        if not ser.is_open:
            ser.open() # use this to break before looping begins
        add_data('which', 'off')
        set_value("status", f"Running: LED off; port: {port}")
        targtime = starttime + get_data('off')*get_data('times')['off'][1]
        oldmousepos = pyautogui.position()
        mouseadd = 3 * 60
        mousetime = starttime + mouseadd
        while time.time() <= endtime:
            mousepos = pyautogui.position()
            if oldmousepos == mousepos and time.time() > mousetime:
                pyautogui.press("shift")
                mousetime = time.time() + mouseadd
            elif time.time() > mousetime:
                mousetime = time.time() + mouseadd
                oldmousepos = pyautogui.position()
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
                    set_value("status", f"Running: LED off; port: {port}")
                    if not ser.is_open:
                        ser.open()
                    sleeptime = get_data('off')*get_data('times')['off'][1] / 100
                elif get_data('which') == 'off':
                    add_data('which', 'on')
                    targtime += get_data('on')*get_data('times')['on'][1]
                    set_value("status", f"Running: LED on; port: {port}")
                    ser.close()
                    sleeptime = get_data('on')*get_data('times')['on'][1] / 100
            set_value("progbar", (time.time() - starttime - pausehold) / (endtime - starttime - pausehold))
            time.sleep(sleeptime)
        if not get_data('cancel'):
            set_value("progbar", 1)
            set_value("status", "Complete")
        # ser.close()
        if not ser.is_open:
            ser.open()
        add_data('running', False)
    except TypeError:
        set_value("settings", "Times not set")
        set_value("status", "Inactive")
    # except IndexError:
    except serial.SerialException:
        set_value("settings", "PORT NOT SET")
        set_value("status", "Inactive")
        add_data("running", False)


def cancel_prog(sender, data):
    add_data('cancel', True)
    if get_data('pause'):
        add_data('pause', False)
        configure_item("Pause", label="Pause")


def pause_prog(sender, data):
    if get_data('pause'):
        add_data('pause', False)
        configure_item("Pause", label="Pause")
    elif get_data('running'):
        add_data('pause', True)
        configure_item("Pause", label="Resume")


def start_cbk(sender, data):
    if not get_data('running'):
        if does_item_exist("progbar"):
            set_value("progbar", 0)
        try:
            run_async_function(loop, data)
        except TypeError:
        # except IndexError:
            set_value("settings", "Times not set")
    else:
        set_value("status", "ALREADY RUNNING")


def mkfalse(sender, data):
    [set_value(ii, False) for ii in get_all_items() if "##" in ii and sender.split("##")[1] in ii and sender != ii]


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            if not ("bluetooth" in port.lower() or "debug" in port.lower() or "wireless" in port.lower()):
            # if not ("debug" in port.lower() or "wireless" in port.lower()):
                s = serial.Serial(port)
                s.close()
                result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def disconnect(sender, data):
    if get_data('ser').is_open:
        ser.close()
    add_data('ser', serial.Serial())
    add_data('port', '')


def setCOM(sender, data):
    add_data('port', sender.split('.')[-1].lstrip('usbserial-'))
    add_data('ser', serial.Serial(sender)) # want to idle in off state

set_global_font_scale(1.2)
set_main_window_size(375, 225)
set_main_window_title("LED Timing GUI")
with window("Main"):
    with menu_bar("Main menu bar"):
        with menu("Settings"):
            with menu("COM port"):
                for port in serial_ports():
                    add_menu_item(port, label=port.split('.')[-1].lstrip('usbserial-'), callback=setCOM)
            add_menu_item("disconnect", label="Disconnect COM", callback=disconnect)

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
    add_progress_bar("progbar", parent="Main", overlay="Progress", width=341) 

    add_data('running', False)
    add_data('ser', serial.Serial())
    add_data('port', '')

start_dearpygui(primary_window="Main")
