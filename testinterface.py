from components import *
from system import *
from model_builder import *
from interface import *
import matlab
import matlab.engine
#%%
var = Varistor()
source = CurrentSourceDC()
switch = CircuitBreaker()
eng = matlab.engine.start_matlab()

# Define the model name
model_name = 'my_simulink_model4'

# Create the model using the `new_system` MATLAB function
eng.new_system(model_name, nargout=0)

# Open the model in Simulink (optional)
eng.open_system(model_name, nargout=0)

# Example: Add a Sine Wave block, a Gain block, and a Scope block
# eng.add_block('simulink/Sources/Sine Wave', f'{model_name}/Sine Wave', nargout=0)
# eng.add_block('simulink/Math Operations/Gain', f'{model_name}/Gain', nargout=0)
# subsystem_path = f'{model_name}/subsys_0'
# eng.add_block('simulink/Ports & Subsystems/Subsystem', subsystem_path, nargout=0)
# eng.add_block(var.directory, f'{model_name}/{var.name}_{var.ID}', nargout=0)
# eng.add_block(source.directory, f'{model_name}/{source.name}_{source.ID}', nargout=0)
# eng.add_block('simulink/Sinks/Scope', f'{model_name}/Scope', nargout=0)
eng.add_block(switch.directory, f'{model_name}/{switch.name}_{switch.ID}', nargout=0)

# Connect the blocks
# eng.add_line(model_name, 'Sine Wave/1', 'Gain/1', nargout=0)
# eng.add_line(model_name, 'Sine Wave/1', 'subsys_0/1', nargout=0)
# eng.add_line(model_name, f'{var.name}_{var.ID}/{var.port[0]}', f'{source.name}_{source.ID}/LConn 1', nargout=0)
# eng.add_line(model_name, f'{var.name}_{var.ID}/{var.port[1]}', f'{source.name}_{source.ID}/RConn 1', nargout=0)
# eng.add_line(model_name, 'Gain/1', 'Scope/1', nargout=0)

# Example: Set the Gain block's gain value to 2
# eng.set_param(f'{model_name}/Gain', 'Gain', '2', nargout=0)
# position_matlab = matlab.double([50, 100, 110, 120])
# eng.set_param(f'{model_name}/Gain', 'Position', position_matlab, nargout=0)
# # eng.set_param(f'{model_name}/{var.name}_{var.ID}', 'prm', '2', nargout=0)
# param_names = eng.get_param(f'{model_name}/{switch.name}_{switch.ID}', 'ObjectParameters')
# possible_values = eng.get_param(f'{model_name}/{switch.name}_{switch.ID}', 'prm_AH', nargout=1)
# eng.set_param(f'{model_name}/{switch.name}_{switch.ID}', 'prm_AH', '2', nargout=0)

# Print the parameter names and their possible values
for param_name, param_value in switch.parameter.items():
    param_value_str = str(param_value) if not isinstance(param_value, str) else param_value
    eng.set_param(f'{model_name}/{switch.name}_{switch.ID}', param_name, param_value_str, nargout=0)

# model_name = 'my_simulink_model4'

# Create the model using the `new_system` MATLAB function
# eng.new_system(model_name, nargout=0)

# Open the model in Simulink (optional)
eng.open_system(model_name, nargout=0)
#%%
eng.add_line(model_name, 'Connection Port/RConn 1', 'subsys_0/LConn1', nargout=0)
# eng.quit()
#%%
handle = eng.get_param(f'{model_name}/subsys_0', 'Handle')
phandel = eng.get_param(handle, 'PortHandles')
#%%
def make_positions(input_list):
    sub_lists = []
    start_index = 0
    odd_count = 1

    while start_index < len(input_list):
        end_index = start_index + odd_count
        sub_list = input_list[start_index:end_index]
        sub_lists.append(sub_list)
        start_index = end_index
        odd_count += 2

    new_input_list = []
    for index, sublist in enumerate(sub_lists):
        for subindex, position in enumerate(sublist):
            new_position = [element + 100 * index for element in position]
            if subindex % 2 == 0:  # Even index (0-based)
                new_position[0] = new_position[0] - (subindex // 2) * 100
                new_position[2] = new_position[0] + 30
            else:  # Odd index (0-based)
                new_position[1] = new_position[1] - ((subindex + 1) // 2) * 100
                new_position[3] = new_position[1] + 30
            new_input_list.append(new_position)
    return new_input_list

def process_string(input_string):
    input_string = input_string.replace('id', '')
    parts = input_string.split('port')
    part_1 = parts[0].rsplit('_', 1)[0]
    part_2 = parts[1]
    return part_1, part_2

def port_sort(item):
    if 'OUT' in item:
        return 0
    elif 'IN' in item:
        return 2
    else:
        return 1
#%%
def add_subsystem_to_simulink(eng, model_name, subsystem):
    # Start a MATLAB Engine session

    # Add a subsystem to the Simulink model
    subsystem_path = f'{model_name}/{subsystem.name}_{subsystem.ID}_{subsystem.subsystem_type}'
    eng.add_block('simulink/Ports & Subsystems/Subsystem', subsystem_path, nargout=0)
    eng.delete_line(subsystem_path, 'In1/1', 'Out1/1', nargout=0)
    eng.delete_block(f'{subsystem_path}/In1', nargout=0)
    eng.delete_block(f'{subsystem_path}/Out1', nargout=0)
    positions = [[100, 100, 130, 130]] * len(subsystem.component_list)
    positions = make_positions(positions)
    for index, component in enumerate(subsystem.component_list):
        eng.add_block(component.directory, f'{subsystem_path}/{component.name}_{component.ID}', nargout=0)
        position_matlab = matlab.double(positions[index])
        eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', 'Position', position_matlab, nargout=0)
        for param_name, param_value in component.parameter.items():
            param_value_str = str(param_value) if not isinstance(param_value, str) else param_value
            eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', param_name, param_value_str, nargout=0)


    # End the MATLAB Engine session


f = DCBuilder()
subsystem = f.create_source_subsystem('voltage', seed=10)

eng = matlab.engine.start_matlab()
model_name = 'my_simulink_model4'

# Create the model using the `new_system` MATLAB function
eng.new_system(model_name, nargout=0)

# Open the model in Simulink (optional)
eng.open_system(model_name, nargout=0)

add_subsystem_to_simulink(eng, model_name, subsystem)
#%%
model_name = 'my_simulink_model4'
eng.add_line(model_name,  'From Workspace/1', 'Simulink-PS Converter/1',nargout=0)
# eng.add_line(model_name, f'{var.name}_{var.ID}/{var.port[0]}', f'{source.name}_{source.ID}/LConn 1', nargout=0)
# eng.add_line(model_name, f'{var.name}_{var.ID}/{var.port[1]}', f'{source.name}_{source.ID}/RConn 1', nargout=0)
# eng.add_line(model_name, 'Gain/1', 'Scope/1', nargout=0)
#%%
param_names = eng.get_param('my_simulink_model4/subsytem_0_source_voltage/ConnectionPort_1', 'ObjectParameters')
#%%
possible_values = eng.get_param('my_simulink_model4/subsytem_0_source_voltage/ConnectionPort_1', 'Side', nargout=1)
eng.set_param('my_simulink_model4/subsytem_0_source_voltage/ConnectionPort_1', 'Side', 'left', nargout=0)
#%%
f = DCBuilder()
f.build_system(seed=2)
sys = f.product()
interf = SystemSimulinkAdapter(sys)
eng = matlab.engine.start_matlab()
model_name = 'my_simulink_model4'
eng.new_system(model_name, nargout=0)
eng.open_system(model_name, nargout=0)
positions = [[100, 100, 130, 130]] * len(sys.subsystem_list)
positions = make_positions(positions)
interf.input_system(eng, model_name)
#%%
interf.change_parameter(eng, model_name, 'Vnom', 20, 'Battery', 0, 'source_battery', 0)
sys.change_component_paramter('vnom', 20, 'Battery', 0, 'source_battery', 0)
#%%
handle = eng.get_param(f'{model_name}/Solver_0', 'Handle')
handle2 = eng.get_param(f'{model_name}/SPDT Switch', 'PortHandles')
s = 'RConn 1'
s1 = s.split(' ')
print(s1[0])
print(int(s1[1]))
p = handle2[s1[0]][0][int(s1[1])-1]
# handle10 = eng.get_param(f'{model_name}/subsytem_switch_8/ConnectionPort_1', 'Handle')
# handles = eng.get_param(f'{model_name}/subsytem_switch_8', 'PortHandles')
# handle1 = eng.get_param(f'{model_name}/Connection Port', 'PortHandles')
# handle2 = eng.get_param(f'{model_name}/Resistor', 'PortHandles')
# print(handle['RConn'])
# phandel = eng.get_param(handle, 'PortHandles')
# eng.add_line(model_name, handle1['RConn'], handle+1, nargout=0)
#%%
model_name = 'D:/paper/simulink/my_simulink_model10_new'
eng = matlab.engine.start_matlab()
# eng.new_system(model_name, nargout=0)
eng.open_system(model_name, nargout=0)
# solver = 'ode45'
# eng.set_param(model_name, 'Solver', solver, nargout=0)
# stop_time = 100
# eng.set_param(model_name, 'StopTime', str(stop_time), nargout=0)
time_values = matlab.double([0])
data_values = matlab.double([[1]])
my_signal = {
    'time': time_values,
    'signals': {
        'values': data_values
    }
}
eng.workspace['simin_0_source_voltage_0'] = eng.struct(my_signal)
#%%
# add lines
path = model_name
connection = ('subsystem_source_battery_id1_inportConnectionPort_1', 'subsystem_source_battery_id0_inportConnectionPort_0')
handles = eng.get_param(f'{model_name}/subsystem_source_battery_0', 'PortHandles')
handll = eng.get_param(f'{model_name}/subsystem_source_battery_0/ConnectionPort_0', 'PortHandles')
#%%
block_1, port_1 = interf.process_string(connection[0])
if 'subsystem' in block_1:
    handle = eng.get_param(f'{path}/{block_1}/{port_1}', 'Handle')
    handle = handle + 1
else:
    handle = eng.get_param(f'{path}/{block_1}', 'PortHandles')
    s = port_1.split(' ')
    if isinstance(handle[s[0]], float):
        handle = handle[s[0]]
    else:
        handle = handle[s[0]][0][int(s[1]) - 1]
block_2, port_2 = interf.process_string(connection[1])
if 'subsystem' in block_2:
    handle_1 = eng.get_param(f'{path}/{block_2}/{port_2}', 'Handle')
    handle_1 = handle_1 + 1
else:
    handle_1 = eng.get_param(f'{path}/{block_2}', 'PortHandles')
    s = port_2.split(' ')
    if isinstance(handle_1[s[0]], float):
        handle_1 = handle_1[s[0]]
    else:
        handle_1 = handle_1[s[0]][0][int(s[1]) - 1]
# handle = eng.get_param(f'{path}/{block_1}/{port_1}', 'Handle')
# handle_1 = eng.get_param(f'{path}/{block_2}/{port_2}', 'Handle')
eng.add_line(path, handle, handle_1, 'autorouting', 'on', nargout=0)