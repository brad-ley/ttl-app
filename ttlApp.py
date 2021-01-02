import time

from dearpygui.core import *
from dearpygui.simple import *


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
    set_value("settings", f"On: {printdict['on']}{timedict['on'][0]}, Off: {printdict['off']}{timedict['off'][0]}, For: {printdict['rep']}{timedict['rep'][0]}")


def loop(sender, data):
    try:
        add_data('cancel', False)
        add_data('pause', False)
        count = 0
        starttime = time.time()
        # endtime = starttime + (get_data('on')*get_data('times')['on'][1] + get_data('off')*get_data('times')['off'][1]) * get_data('rep')*get_data('times')['rep'][1]
        endtime = starttime + get_data('rep')*get_data('times')['rep'][1]
        add_data('running', True)
        pausehold = 0
        targtime = starttime + get_data('on')*get_data('times')['on'][1]
        add_data('which', 'on')
        sleeptime = get_data('on')*get_data('times')['on'][1] / 100
        set_value("status", "Running: LED on")
        while time.time() <= endtime:
            if get_data('cancel'):
                set_value("status", "Cancelled")
                break
            if get_data('pause'):
                pausestart = time.time()
                while True:
                    set_value("status", "Paused")
                    if not get_data('pause'):
                        pausehold += time.time() - pausestart
                        endtime += time.time() - pausestart
                        break
            if time.time() > targtime:
                if get_data('which') == 'on':
                    add_data('which', 'off')
                    targtime += get_data('off')*get_data('times')['off'][1]
                    set_value("status", "Running: LED off")
                    sleeptime = get_data('off')*get_data('times')['off'][1] / 100
                elif get_data('which') == 'off':
                    add_data('which', 'on')
                    targtime += get_data('on')*get_data('times')['on'][1]
                    set_value("status", "Running: LED on")
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


def pause_prog(sender, data):
    if get_data('pause'):
        add_data('pause', False)
        configure_item("Pause", label="Pause")
    elif get_data('running'):
    # if not get_data('pause') and get_data('running'):
    # else:
        add_data('pause', True)
        configure_item("Pause", label="Resume")


def start_cbk(sender, data):
    if does_item_exist("progbar"):
        set_value("progbar", 0)
    try:
        run_async_function(loop, data)
    except TypeError:
    # except IndexError:
        set_value("settings", "Times not set")


def mkfalse(sender, data):
    [set_value(ii, False) for ii in get_all_items() if "##" in ii and sender.split("##")[1] in ii and sender != ii]

set_global_font_scale(1.2)
set_main_window_size(375, 200)
set_main_window_title("LED Timing GUI")
with window("Main"):
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
    add_checkbox('s##rep', default_value=True, callback=mkfalse, label="sec")
    add_same_line(spacing=10)
    add_checkbox('min##rep', default_value=False, callback=mkfalse, label="min")
    add_same_line(spacing=10)
    add_checkbox('hr##rep', default_value=False, callback=mkfalse, label="hour")
    add_label_text("settings", default_value=f"On: not set, Off: not set, For: not set")
    add_label_text("status", default_value=f"Inactive")
    add_progress_bar("progbar", parent="Main", overlay="Progress", width=341) 

start_dearpygui(primary_window="Main")
