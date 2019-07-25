import sys

import pyRigolDP832 as dp
import pyvisa as visa
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Button, TextInput, Select
from bokeh.plotting import figure


def voltage_handler(attr, old, new):
    my_supply.set_voltage(voltage_control.value)


def comment_handler(attr, old, new):
    change = comment_box.value + ","
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
    change = str(length).strip() + "," + str(voltage).strip() + "," + str(current).strip() + ","
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
    save_file = file_control.value
    f = open(save_file)


def apply_settings():
    my_supply.apply_all()
    my_supply.apply_ocp()


def start_button_handler():
    curdoc().add_periodic_callback(plot_update, 200)


save_file = ''
rm = visa.ResourceManager()
print(rm)
print("Current resources: ")
print(rm.list_resources())
f = open('readings.csv', 'a')
try:
    iface = rm.open_resource("TCPIP::192.168.1.111::INSTR")
    my_supply = dp.RigolDP832(iface)
    print("Connected to " + my_supply.IDN)

except Exception:
    print("Unable to connect.")
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
file_control = TextInput(title='Path to save file', value='readings.csv')
comment_box = TextInput(title='Annotation (Will add when box is unselected)')
start_button = Button(label='Start recording data')
plot1 = figure(x_range=(0, 10000), y_range=(0, 30), x_axis_label='Time (100 ms)', y_axis_label='Volts',
               title='Voltage over time', plot_width=500, plot_height=200)
plot2 = figure(x_range=(0, 10000), y_range=(0, 3.5), x_axis_label='Time (100 ms)', y_axis_label='Amps',
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
comment_box.on_change('value', comment_handler)
channel_dropdown.on_change('value', channel_handler)
start_button.on_click(start_button_handler)
curdoc().add_periodic_callback(plot_update, 100)
curdoc().add_root(row(column(current_control, voltage_control, power_control, ocp_control, channel_dropdown),
                      column(apply_button, start_button, file_control, comment_box, plot1, plot2)))
