import sys
import time
import pyRigolDP832 as dp
import pyvisa as visa
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Button, TextInput, Select, MultiSelect
from bokeh.plotting import figure
import datetime
import os
import csv

supplies = []


def voltage_handler(attr, old, new):
    my_supply.set_voltage(voltage_control.value)


def comment_handler(attr, old, new):
    change = comment_box.value + "\n"
    with open(file_control.value, 'a') as f:
        f.write(change)
        f.close()


def plot_update():
    global voltages1
    global voltages2
    global voltages3
    global voltages4
    global voltages5
    global voltages6
    global currents1
    global currents2
    global currents3
    global currents4
    global currents5
    global currents6

    x.append(len(x))
    try:
        voltages1.append(supplies[0].set_channel(1).get_voltage())
    except Exception:
        pass
    try:
        currents1.append(supplies[0].get_current())
    except Exception:
        pass
    try:
        voltages2.append(supplies[0].set_channel(2).get_voltage())
    except Exception:
        pass
    try:
        currents2.append(supplies[0].get_current())
    except Exception:
        pass
    try:
        voltages3.append(supplies[0].set_channel(3).get_voltage())
    except Exception:
        pass
    try:
        currents3.append(supplies[0].get_current())
    except Exception:
        pass
    try:
        voltages4.append(supplies[1].set_channel(1).get_voltage())
    except Exception:
        pass
    try:
        currents4.append(supplies[1].get_current())
    except Exception:
        pass
    try:
        voltages5.append(supplies[1].set_channel(2).get_voltage())
    except Exception:
        pass
    try:
        currents5.append(supplies[1].get_current())
    except Exception:
        pass
    try:
        voltages6.append(supplies[1].set_channel(3).get_voltage())
    except Exception:
        pass
    try:
        currents6.append(supplies[1].get_current())
    except Exception:
        pass
    try:
        voltages7.append(supplies[2].set_channel(1).get_voltage())
    except Exception:
        pass
    try:
        currents7.append(supplies[2].get_current())
    except Exception:
        pass
    try:
        voltages8.append(supplies[2].set_channel(2).get_voltage())
    except Exception:
        pass
    try:
        currents8.append(supplies[2].get_current())
    except Exception:
        pass
    try:
        voltages9.append(supplies[2].set_channel(3).get_voltage())
    except Exception:
        pass
    try:
        currents9.append(supplies[2].get_current())
    except Exception:
        pass

    length = len(x)
    source.data = dict(x=x, voltages1=voltages1, currents1=currents1)
    time_change = time.time() - t0
    change = str(length).strip() + "," + str(time_change).strip() + "," + str(
        datetime.datetime.now()).strip() + "," + voltages1[len(voltages1) - 1] + "," + currents1[len(currents1) - 1] + \
             voltages2[len(voltages2) - 1] + currents2[len(currents2) - 1] + voltages3[len(voltages3) - 1] + currents3[
                 len(currents3) - 1] + voltages4[len(voltages4) - 1] + currents4[len(currents4) - 1] + voltages5[
                 len(voltages5) - 1] + currents5[len(currents5) - 1] + voltages6[len(voltages6) - 1] + currents6[
                 len(currents6) - 1] + voltages7[len(voltages7) - 1] + currents7[len(currents7) - 1] + voltages8[
                 len(voltages8) - 1] + currents8[len(currents8) - 1] + voltages9[len(voltages9) - 1] + currents9[
                 len(currents9) - 1]

    with open(file_control.value, 'a') as f:
        # writer = csv.writer(f)
        f.write(change)
        f.close()


def current_handler(attr, old, new):
    my_supply.set_current(current_control.value)


def power_handler(attr, old, new):
    my_supply.set_power(power_control.value)


def supply_dropdown_handler(attr, old, new):
    global my_supply
    global supplies
    for supply in supplies:
        if supply.IDN is supply_dropdown.value:
            my_supply = supply
            break


def ocp_handler(attr, old, new):
    my_supply.set_ocp(ocp_control.value)


def channel_handler(attr, old, new):
    if channel_dropdown.value == '1':
        my_supply.set_channel('ch1')
    elif channel_dropdown.value == '2':
        my_supply.set_channel('ch2')
    else:
        my_supply.set_channel('ch3')

def multiselect_handler(attr, old, new):
    supply_textbox.value = supply_dropdown.value[0]


def connect_button_handler():
    global supplies
    rm = visa.ResourceManager('@py')
    try:
        iface = rm.open_resource(supply_textbox.value, write_termination='\n', read_termination='\n')
        my_supply = dp.RigolDP832(iface)
        print("Connected to " + my_supply.IDN)
    except Exception as ex:
        print("Unable to connect.", ex)
        sys.exit()

    cmd_rdy = my_supply.ready_for_command()
    if int(cmd_rdy) is int(1):
        print("The supply is ready to recieve commands")
    else:
        print("The supply is NOT ready")
        print(cmd_rdy)
    supplies.append(my_supply)
    ips = []
    for supply in supplies:
        ips.append(supply.IDN)
    supply_dropdown.options = ips
    settings = open("settings.csv", 'a+')
    settings.write(str(ips[len(ips) - 1]))


def file_handler(attr, old, new):
    if not os.path.exists(directory_control.value):
        os.mkdir(directory_control.value)
    save_file = os.path.join(directory_control.value, file_control.value)
    try:
        f = open(save_file, "a+")
    except Exception:
        f = open(save_file, "a")
    f.write("Index,Time Stamp,Date Stamp,Voltage,Current")
    f.close()


def apply_settings():
    my_supply.apply_all()
    my_supply.apply_ocp()


callback_id = None


def start_button_handler():
    global callback_id
    if start_button.label == 'Start recording data':
        callback_id = curdoc().add_periodic_callback(plot_update, 150)
        start_button.label = 'Stop recording data'
    else:
        start_button.label = 'Start recording data'
        curdoc().remove_periodic_callback(callback_id)


save_file = ''
f = open('readings.csv', 'a+')
f.write("Index,Time Stamp,Date Stamp,Supply 1 Channel 1 Voltage,Supply 1 Channel 1 Current,Supply 1 Channel 2 Voltage,"
        "Supply 1 Channel 2 Current,Supply 1 Channel 3 Voltage,Supply 1 Channel 3 Current, Supply 2 Channel 1 Voltage,"
        "Supply 2 Channel 1 Current,Supply 2 Channel 2 Voltage,Supply 2 Channel 2 Current,Supply 2 Channel 3 Voltage,"
        "Supply 2 Channel 3 Current,Supply 3 Channel 1 Voltage, Supply 3 Channel 1 Current,Supply 3 Channel 2 Voltage,"
        "Supply 3 Channel 2 Current,Supply 3 Channel 3 Voltage, Supply 3 Channel 3 Current\n")
f.flush()
my_supply = None

supplies_from_file = open('settings.csv', 'r+')
read = csv.reader(supplies_from_file)
supplies_load = []
for val in read:
    for subval in val:
        supplies_load.append(subval)
apply_button = Button(label='Apply settings')
current_control = TextInput(title='Current control (A)')
ip_control_textbox = TextInput(title='Enter your device\'s IP address')
connect_button = Button(label='Connect to device')
voltage_control = TextInput(title='Voltage control (V)')
power_control = TextInput(title='Power control (W)')
channel_dropdown = Select(title='Channel control', options=['1', '2', '3'])
supply_textbox = TextInput(title='Current supply')
supply_dropdown = MultiSelect(options=supplies_load)
ocp_control = TextInput(title='OCP control (A)')
file_control = TextInput(title='Desired name of save file', value='readings.csv')
directory_control = TextInput(title="Absolute path to desired directory (Ex: /home/pi/Documents)")
comment_box = TextInput(title='Annotation (Will add when box is unselected)')
start_button = Button(label='Start recording data')
PS1C1Voltage = figure(x_range=(0, 300), y_range=(0, 30), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 1 Channel 1 Voltage over time', plot_width=300, plot_height=150)
PS1C1Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 1 Channel 1 Current over time', plot_width=300, plot_height=150)

PS1C2Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 1 Channel 2 Voltage over time', plot_width=300, plot_height=150)

PS1C2Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 1 Channel 2 Current over time', plot_width=300, plot_height=150)

PS1C3Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 1 Channel 3 Voltage over time', plot_width=300, plot_height=150)

PS1C3Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 1 Channel 3 Current over time', plot_width=300, plot_height=150)

PS2C1Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 2 Channel 1 Voltage over time', plot_width=300, plot_height=150)

PS2C1Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 2 Channel 1 Current over time', plot_width=300, plot_height=150)

PS2C2Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 2 Channel 2 Voltage over time', plot_width=300, plot_height=150)

PS2C2Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 2 Channel 2 Current over time', plot_width=300, plot_height=150)

PS2C3Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 2 Channel 3 Voltage over time', plot_width=300, plot_height=150)

PS2C3Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 2 Channel 3 Current over time', plot_width=300, plot_height=150)
PS3C1Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 3 Channel 1 Voltage over time', plot_width=300, plot_height=150)
PS3C1Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 3 Channel 1 Current over time', plot_width=300, plot_height=150)
PS3C2Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 3 Channel 2 Voltage over time', plot_width=300, plot_height=150)
PS3C2Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 3 Channel 2 Current over time', plot_width=300, plot_height=150)
PS3C3Voltage = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Volts',
                      title='Power Supply 3 Channel 3 Voltage over time', plot_width=300, plot_height=150)
PS3C3Current = figure(x_range=(0, 300), y_range=(0, 3.5), x_axis_label='Time (150 ms)', y_axis_label='Amps',
                      title='Power Supply 3 Channel 3 Current over time', plot_width=300, plot_height=150)

x = []
voltages1 = []
voltages2 = []
voltages3 = []
voltages4 = []
voltages5 = []
voltages6 = []
voltages7 = []
voltages8 = []
voltages9 = []
currents1 = []
currents2 = []
currents3 = []
currents4 = []
currents5 = []
currents6 = []
currents7 = []
currents8 = []
currents9 = []

source = ColumnDataSource({
    'x': x,
    'voltages1': voltages1,
    'voltages2': voltages2,
    'voltages3': voltages3,
    'voltages4': voltages4,
    'voltages5': voltages5,
    'voltages6': voltages6,
    'voltages7': voltages7,
    'voltages8': voltages8,
    'voltages9': voltages9,
    'currents1': currents1,
    'currents2': currents2,
    'currents3': currents3,
    'currents4': currents4,
    'currents5': currents5,
    'currents6': currents6,
    'currents7': currents7,
    'currents8': currents8,
    'currents9': currents9
})
PS1C1Voltage.line(x='x', y='voltages1', source=source)
PS1C1Current.line(x='x', y='currents1', source=source)
PS1C2Voltage.line(x='x', y='voltages2', source=source)
PS1C2Current.line(x='x', y='currents2', source=source)
PS1C3Voltage.line(x='x', y='voltages3', source=source)
PS1C3Current.line(x='x', y='currents3', source=source)
PS2C1Voltage.line(x='x', y='voltages4', source=source)
PS2C1Current.line(x='x', y='currents4', source=source)
PS2C2Voltage.line(x='x', y='voltages5', source=source)
PS2C2Current.line(x='x', y='currents5', source=source)
PS2C3Voltage.line(x='x', y='voltages6', source=source)
PS2C3Current.line(x='x', y='currents6', source=source)
PS3C1Current.line(x='x', y='currents7', source=source)
PS3C1Voltage.line(x='x', y='voltages7', source=source)
PS3C2Current.line(x='x', y='currents8', source=source)
PS3C2Voltage.line(x='x', y='voltages8', source=source)
PS3C3Current.line(x='x', y='currents9', source=source)
PS3C3Voltage.line(x='x', y='voltages9', source=source)

file_control.on_change('value', file_handler)
apply_button.on_click(apply_settings)
current_control.on_change('value', current_handler)
voltage_control.on_change('value', voltage_handler)
power_control.on_change('value', power_handler)
ocp_control.on_change('value', ocp_handler)
file_control.on_change('value', file_handler)
directory_control.on_change('value', file_handler)
comment_box.on_change('value', comment_handler)
channel_dropdown.on_change('value', channel_handler)
start_button.on_click(start_button_handler)
connect_button.on_click(connect_button_handler)
supply_dropdown.on_change('value', multiselect_handler)
t0 = time.time()
curdoc().add_root(row(
    column(supply_textbox, supply_dropdown, connect_button, current_control, voltage_control, power_control,
           ocp_control, channel_dropdown, apply_button, directory_control, file_control, start_button, comment_box),
    column(PS1C1Current, PS1C1Voltage, PS1C2Current, PS1C2Voltage, PS1C3Current, PS1C3Voltage),
    column(PS2C1Current, PS2C1Voltage, PS2C2Current, PS2C2Voltage, PS2C3Current, PS2C3Voltage),
    column(PS3C1Current, PS3C1Voltage, PS3C2Current, PS3C2Voltage, PS3C3Current, PS3C3Voltage)))
