import sys
import time
import pyRigolDP832 as dp
import pyvisa as visa
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Button, TextInput, Select
from bokeh.plotting import figure
import datetime
import os

def voltage_handler(attr, old, new):
    my_supply.set_voltage(voltage_control.value)


def comment_handler(attr, old, new):
    change = comment_box.value + "\n"
    with open(file_control.value, 'a') as f:
        f.write(change)
        f.close()


def plot_update():
    global voltages
    global currents
    x.append(len(x))
    voltage = my_supply.get_voltage()
    current = my_supply.get_current()
    voltages.append(voltage)
    currents.append(current)
    length = len(x)
    source.data = dict(x=x, voltages=voltages, currents=currents)
    time_change = time.time() - t0
    change = str(length).strip() + "," + str(time_change).strip() + "," + str(datetime.datetime.now()).strip() + "," + str(voltage).strip() + "," + str(current).strip() + "\n"
    with open(file_control.value, 'a') as f:
        # writer = csv.writer(f)
        f.write(change)
        f.close()


def current_handler(attr, old, new):
    my_supply.set_current(current_control.value)


def power_handler(attr, old, new):
    my_supply.set_power(power_control.value)


def ocp_handler(attr, old, new):
    my_supply.set_ocp(ocp_control.value)


def channel_handler(attr, old, new):
    if channel_dropdown.value == '1':
        my_supply.set_channel('ch1')
    elif channel_dropdown.value == '2':
        my_supply.set_channel('ch2')
    else:
        my_supply.set_channel('ch3')


def file_handler(attr, old, new):
    if not os.path.exists(directory_control.value):
        os.mkdir(directory_control.value)
    save_file = os.path.join(directory_control.value, file_control.value)
    try:
        f = open(save_file, "a+")
    except Exception:
        f = open(save-file, "a")
    f.write("Index,Time Stamp,Date Stamp,Voltage,Current")
    f.close()

def apply_settings():
    my_supply.apply_all()
    my_supply.apply_ocp()

callback_id = None


def start_button_handler():
    global callback_id
    if start_button.label == 'Start recording data':
        callback_id = curdoc().add_periodic_callback(plot_update, 100)
        start_button.label = 'Stop recording data'
    else:
        start_button.label = 'Start recording data'
        curdoc().remove_periodic_callback(callback_id)

save_file = ''
rm = visa.ResourceManager('@py')
print(rm)
print("Current resources: ")
print(rm.list_resources())
f = open('readings.csv', 'a')
f.write("Index,Time Stamp,Date Stamp,Voltage,Current\n")
f.flush()
try:
    iface = rm.open_resource("TCPIP::192.168.1.111::INSTR",  write_termination='\n',read_termination='\n')
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

apply_button = Button(label='Apply settings')
current_control = TextInput(title='Current control (A)')
voltage_control = TextInput(title='Voltage control (V)')
power_control = TextInput(title='Power control (W)')
channel_dropdown = Select(title='Channel control', options=['1', '2', '3'])
ocp_control = TextInput(title='OCP control (A)')
file_control = TextInput(title='Desired name of save file', value='readings.csv')
directory_control = TextInput(title="Absolute path to desired directory (Ex: /home/pi/Documents)")
comment_box = TextInput(title='Annotation (Will add when box is unselected)')
start_button = Button(label='Start recording data')
plot1 = figure(x_range=(0, 500), y_range=(0, 30), x_axis_label='Time (100 ms)', y_axis_label='Volts',
               title='Voltage over time', plot_width=500, plot_height=200)
plot2 = figure(x_range=(0, 500), y_range=(0, 3.5), x_axis_label='Time (100 ms)', y_axis_label='Amps',
               title='Current over time', plot_width=500, plot_height=200)
x = []
voltages = []
currents = []
source = ColumnDataSource({
    'x': x,
    'voltages': voltages,
    'currents': currents
})
plot1.line(x='x', y='voltages', source=source)
plot2.line(x='x', y='currents', source=source)
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
t0 = time.time()
curdoc().add_root(row(column(current_control, voltage_control, power_control, ocp_control, channel_dropdown),
                      column(apply_button, directory_control, file_control, start_button, comment_box, plot1, plot2)))
