
from components import *
from system import *
from model_builder import *
from interface import *
from abstract_factory import *
import matlab
import matlab.engine
#%%
f = DCBuilder()
f.build_system(seed=2)
sys = f.product()
# interf = SystemSimulinkAdapter(sys)
# eng = matlab.engine.start_matlab()
# model_name = 'my_simulink_model4'
# eng.new_system(model_name, nargout=0)
# eng.open_system(model_name, nargout=0)
# interf.input_system(eng, model_name)
#%%
sensor_subsys_group = {}
for subsys in sys.subsystem_list:
    if 'sensor' in subsys.subsystem_type:
        sensor_group = {}
        for component in subsys.component_list:
            if component.component_type == 'Sensor':
                if component.name in sensor_group:
                    sensor_group[component.name].append(component)
                else:
                    sensor_group[component.name] = [component]
        sensor_subsys_group[f'{subsys.subsystem_type}_{subsys.ID}'] = sensor_group

#%%
def create_upgrade_component(name, categary):
    component_factory = ElectriaclComponentFactory()
    comp = component_factory.create_component(name, categary, randomattr=False)
    comp.name = comp.name + 'Upgrade'
    return comp
keys = list(sensor_subsys_group.keys())
subsys_key = random.choice(keys)
sensor_group = sensor_subsys_group[subsys_key]
key = subsys_key.rsplit('_', 1)
#%%
#C+S
for subsys in sys.subsystem_list:
    num_to_workspace = 0
    if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
        for name, sensors_list in sensor_group.items():
            if name == 'CurrentSensor':
                even_integer = random.randrange(4, 9, 2)
                logic = create_upgrade_component('Sparing', Logic)
                mux_signal = create_upgrade_component('Mux', Utilities)
                mux = create_upgrade_component('Mux', Utilities)
                mux_signal.set_input(int(even_integer/2))
                mux.set_input(int(even_integer/2))
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux_signal, mux, to_workspace)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux_signal.get_port_info()[-1]))
                subsys.add_connection((logic.get_port_info()[1], mux.get_port_info()[-1]))
                length = len(sensors_list)
                cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
                if length < even_integer:
                    for i in range(even_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
                        for connection in old_connect[0]:
                            remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
                            subsys.connections.remove(connection)
                            subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
                        subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
                                               cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
                        cunrrent_sensors.append(sensor)
                    sensor_new_list = cunrrent_sensors
                else:
                    sensor_new_list = random.sample(cunrrent_sensors, even_integer)
                new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in range(0, len(sensor_new_list), 2)]
                for i, new_pair in enumerate(new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    subsys.add_component(comparator)
                    subsys.add_connection((comparator.get_port_info()[-1], mux.get_port_info()[i]))
                    for n, new_sensor in enumerate(new_pair):
                        port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                        converter = create_upgrade_component('PSSimuConv', Utilities)
                        subsys.add_component(converter)
                        if n == 0:
                            subsys.add_connection((converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                        subsys.add_connection((converter.get_port_info()[-1], comparator.get_port_info()[n]))
                        subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
            if name == 'VoltageSensor':
                even_integer = random.randrange(4, 9, 2)
                logic = create_upgrade_component('Sparing', Logic)
                mux_signal = create_upgrade_component('Mux', Utilities)
                mux = create_upgrade_component('Mux', Utilities)
                mux_signal.set_input(int(even_integer/2))
                mux.set_input(int(even_integer/2))
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux_signal, mux, to_workspace)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux_signal.get_port_info()[-1]))
                subsys.add_connection((logic.get_port_info()[1], mux.get_port_info()[-1]))
                length = len(sensors_list)
                voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
                if length < even_integer:
                    for i in range(even_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
                                                                 voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
                        for n, connections in enumerate(old_connect):
                            for connection in connections:
                                remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(n+1)].replace('+', '').replace('-', '')]
                                subsys.add_connection((sensor.get_port_info()[-(n+1)].replace('+', '').replace('-', ''), remain_port[0]))
                        voltage_sensors.append(sensor)
                    sensor_new_list = voltage_sensors
                else:
                    sensor_new_list = random.sample(voltage_sensors, even_integer)
                new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in range(0, len(sensor_new_list), 2)]
                for i, new_pair in enumerate(new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    subsys.add_component(comparator)
                    subsys.add_connection((comparator.get_port_info()[-1], mux.get_port_info()[i]))
                    for n, new_sensor in enumerate(new_pair):
                        port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                        converter = create_upgrade_component('PSSimuConv', Utilities)
                        subsys.add_component(converter)
                        if n == 0:
                            subsys.add_connection((converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                        subsys.add_connection((converter.get_port_info()[-1], comparator.get_port_info()[n]))
                        subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
#C+V
for subsys in sys.subsystem_list:
    num_to_workspace = 0
    if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
        for name, sensors_list in sensor_group.items():
            if name == 'CurrentSensor':
                odd_integer = random.randrange(3, 6, 2)
                logic = create_upgrade_component('Voter', Logic)
                mux = create_upgrade_component('Mux', Utilities)
                mux.set_input(odd_integer)
                signal = create_upgrade_component('Constant', Signal)
                signal.value = 'nan'
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux, to_workspace, signal)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                length = len(sensors_list)
                cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
                if length < odd_integer*2:
                    for i in range(odd_integer*2 - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
                        for connection in old_connect[0]:
                            remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
                            subsys.connections.remove(connection)
                            subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
                        subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
                                               cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
                        cunrrent_sensors.append(sensor)
                    sensor_new_list = cunrrent_sensors
                else:
                    sensor_new_list = random.sample(cunrrent_sensors, odd_integer*2)
                new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in range(0, len(sensor_new_list), 2)]
                for i, new_pair in enumerate(new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    switch = create_upgrade_component('CommonSwitch', Utilities)
                    subsys.add_component(comparator, switch)
                    subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                    subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                    subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                    for n, new_sensor in enumerate(new_pair):
                        port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                        converter = create_upgrade_component('PSSimuConv', Utilities)
                        subsys.add_component(converter)
                        if n == 0:
                            subsys.add_connection((converter.get_port_info()[-1], switch.get_port_info()[0]))
                        subsys.add_connection((converter.get_port_info()[-1], comparator.get_port_info()[n]))
                        subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
            if name == 'VoltageSensor':
                odd_integer = random.randrange(3, 6, 2)
                logic = create_upgrade_component('Voter', Logic)
                mux = create_upgrade_component('Mux', Utilities)
                mux.set_input(odd_integer)
                signal = create_upgrade_component('Constant', Signal)
                signal.value = 'nan'
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux, to_workspace, signal)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                length = len(sensors_list)
                voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
                if length < odd_integer*2:
                    for i in range(odd_integer*2 - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
                                                                 voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
                        for n, connections in enumerate(old_connect):
                            for connection in connections:
                                remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(n+1)].replace('+', '').replace('-', '')]
                                subsys.add_connection((sensor.get_port_info()[-(n+1)].replace('+', '').replace('-', ''), remain_port[0]))
                        voltage_sensors.append(sensor)
                    sensor_new_list = voltage_sensors
                else:
                    sensor_new_list = random.sample(voltage_sensors, odd_integer*2)
                new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in range(0, len(sensor_new_list), 2)]
                for i, new_pair in enumerate(new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    switch = create_upgrade_component('CommonSwitch', Utilities)
                    subsys.add_component(comparator, switch)
                    subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                    subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                    subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                    for n, new_sensor in enumerate(new_pair):
                        port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                        converter = create_upgrade_component('PSSimuConv', Utilities)
                        subsys.add_component(converter)
                        if n == 0:
                            subsys.add_connection((converter.get_port_info()[-1], switch.get_port_info()[0]))
                        subsys.add_connection((converter.get_port_info()[-1], comparator.get_port_info()[n]))
                        subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
#V+C+S
for subsys in sys.subsystem_list:
    num_to_workspace = 0
    if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
        for name, sensors_list in sensor_group.items():
            if name == 'CurrentSensor':
                num_integer = random.randrange(3, 7, 1)
                odd_integer = random.randrange(3, num_integer+1, 2)
                voter = create_upgrade_component('Voter', Logic)
                spare = create_upgrade_component('Sparing', Logic)
                spare.n = odd_integer
                mux_signal = create_upgrade_component('Mux', Utilities)
                mux_error = create_upgrade_component('Mux', Utilities)
                mux_signal.set_input(num_integer)
                mux_error.set_input(num_integer)
                demux = create_upgrade_component('Demux', Utilities)
                mux = create_upgrade_component('Mux', Utilities)
                demux.set_output(odd_integer)
                mux.set_input(odd_integer)
                delay_out = create_upgrade_component('UnitDelay', Utilities)
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(voter, spare, mux_signal, mux_error, mux, demux, to_workspace, delay_out)
                subsys.add_connection((voter.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((voter.get_port_info()[-1], delay_out.get_port_info()[0]))
                subsys.add_connection((voter.get_port_info()[0], mux.get_port_info()[-1]))
                for i in range(odd_integer):
                    subsys.add_connection((demux.get_port_info()[(i+1)], mux.get_port_info()[i]))
                subsys.add_connection((spare.get_port_info()[-1], demux.get_port_info()[0]))
                subsys.add_connection((mux_signal.get_port_info()[-1], spare.get_port_info()[0]))
                subsys.add_connection((mux_error.get_port_info()[-1], spare.get_port_info()[1]))
                length = len(sensors_list)
                cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
                if length < num_integer:
                    for i in range(num_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
                        for connection in old_connect[0]:
                            remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
                            subsys.connections.remove(connection)
                            subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
                        subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
                                               cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
                        cunrrent_sensors.append(sensor)
                    sensor_new_list = cunrrent_sensors
                else:
                    sensor_new_list = random.sample(cunrrent_sensors, num_integer)
                for i, new_sensor in enumerate(sensor_new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    delay = create_upgrade_component('UnitDelay', Utilities)
                    subsys.add_component(comparator, delay)
                    subsys.add_connection((comparator.get_port_info()[-1], mux_error.get_port_info()[i]))
                    port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                    converter = create_upgrade_component('PSSimuConv', Utilities)
                    subsys.add_component(converter)
                    subsys.add_connection((converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                    subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                    subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                    subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                    subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
            if name == 'VoltageSensor':
                num_integer = random.randrange(3, 7, 1)
                odd_integer = random.randrange(3, num_integer+1, 2)
                voter = create_upgrade_component('Voter', Logic)
                spare = create_upgrade_component('Sparing', Logic)
                spare.n = odd_integer
                mux_signal = create_upgrade_component('Mux', Utilities)
                mux_error = create_upgrade_component('Mux', Utilities)
                mux_signal.set_input(num_integer)
                mux_error.set_input(num_integer)
                demux = create_upgrade_component('Demux', Utilities)
                mux = create_upgrade_component('Mux', Utilities)
                demux.set_output(odd_integer)
                mux.set_input(odd_integer)
                delay_out = create_upgrade_component('UnitDelay', Utilities)
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(voter, spare, mux_signal, mux_error, mux, demux, to_workspace, delay_out)
                subsys.add_connection((voter.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((voter.get_port_info()[-1], delay_out.get_port_info()[0]))
                subsys.add_connection((voter.get_port_info()[0], mux.get_port_info()[-1]))
                for i in range(odd_integer):
                    subsys.add_connection((demux.get_port_info()[-(i+1)], mux.get_port_info()[i]))
                subsys.add_connection((spare.get_port_info()[-1], demux.get_port_info()[0]))
                subsys.add_connection((mux_signal.get_port_info()[-1], spare.get_port_info()[0]))
                subsys.add_connection((mux_error.get_port_info()[-1], spare.get_port_info()[1]))
                length = len(sensors_list)
                voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
                if length < odd_integer:
                    for i in range(odd_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
                                                                 voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
                        for n, connections in enumerate(old_connect):
                            for connection in connections:
                                remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(n+1)].replace('+', '').replace('-', '')]
                                subsys.add_connection((sensor.get_port_info()[-(n+1)].replace('+', '').replace('-', ''), remain_port[0]))
                        voltage_sensors.append(sensor)
                    sensor_new_list = voltage_sensors
                else:
                    sensor_new_list = random.sample(voltage_sensors, odd_integer)
                for i, new_sensor in enumerate(sensor_new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    delay = create_upgrade_component('UnitDelay', Utilities)
                    subsys.add_component(comparator, delay)
                    subsys.add_connection((comparator.get_port_info()[-1], mux_error.get_port_info()[i]))
                    port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                    converter = create_upgrade_component('PSSimuConv', Utilities)
                    subsys.add_component(converter)
                    subsys.add_connection((converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                    subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                    subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                    subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                    subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
#V+C
for subsys in sys.subsystem_list:
    num_to_workspace = 0
    if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
        for name, sensors_list in sensor_group.items():
            if name == 'CurrentSensor':
                odd_integer = random.randrange(3, 6, 2)
                logic = create_upgrade_component('Voter', Logic)
                mux = create_upgrade_component('Mux', Utilities)
                delay_out = create_upgrade_component('UnitDelay', Utilities)
                mux.set_input(odd_integer)
                signal = create_upgrade_component('Constant', Signal)
                signal.value = 'nan'
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux, to_workspace, signal, delay_out)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[-1], delay_out.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                length = len(sensors_list)
                cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
                if length < odd_integer:
                    for i in range(odd_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
                        for connection in old_connect[0]:
                            remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
                            subsys.connections.remove(connection)
                            subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
                        subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
                                               cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
                        cunrrent_sensors.append(sensor)
                    sensor_new_list = cunrrent_sensors
                else:
                    sensor_new_list = random.sample(cunrrent_sensors, odd_integer)
                for i, new_sensor in enumerate(sensor_new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    switch = create_upgrade_component('CommonSwitch', Utilities)
                    delay = create_upgrade_component('UnitDelay', Utilities)
                    subsys.add_component(comparator, switch, delay)
                    subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                    subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                    subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                    port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                    converter = create_upgrade_component('PSSimuConv', Utilities)
                    subsys.add_component(converter)
                    subsys.add_connection((converter.get_port_info()[-1], switch.get_port_info()[0]))
                    subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                    subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                    subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                    subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
            if name == 'VoltageSensor':
                odd_integer = random.randrange(3, 6, 2)
                logic = create_upgrade_component('Voter', Logic)
                mux = create_upgrade_component('Mux', Utilities)
                delay_out = create_upgrade_component('UnitDelay', Utilities)
                mux.set_input(odd_integer)
                signal = create_upgrade_component('Constant', Signal)
                signal.value = 'nan'
                to_workspace = create_upgrade_component('ToWorkspace', Workspace)
                to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                num_to_workspace += 1
                subsys.add_component(logic, mux, to_workspace, signal, delay_out)
                subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[-1], delay_out.get_port_info()[0]))
                subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                length = len(sensors_list)
                voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
                if length < odd_integer:
                    for i in range(odd_integer - length):
                        sensor = create_upgrade_component(name, ElectricalSensor)
                        subsys.add_component(sensor)
                        old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
                                                                 voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
                        for n, connections in enumerate(old_connect):
                            for connection in connections:
                                remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(n+1)].replace('+', '').replace('-', '')]
                                subsys.add_connection((sensor.get_port_info()[-(n+1)].replace('+', '').replace('-', ''), remain_port[0]))
                        voltage_sensors.append(sensor)
                    sensor_new_list = voltage_sensors
                else:
                    sensor_new_list = random.sample(voltage_sensors, odd_integer)
                for i, new_sensor in enumerate(sensor_new_list):
                    comparator = create_upgrade_component('Comparator', Logic)
                    switch = create_upgrade_component('CommonSwitch', Utilities)
                    delay = create_upgrade_component('UnitDelay', Utilities)
                    subsys.add_component(comparator, switch, delay)
                    subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                    subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                    subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                    port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                    converter = create_upgrade_component('PSSimuConv', Utilities)
                    subsys.add_component(converter)
                    subsys.add_connection((converter.get_port_info()[-1], switch.get_port_info()[0]))
                    subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                    subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                    subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                    subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
interf = SystemSimulinkAdapter(sys)
eng = matlab.engine.start_matlab()
model_name = 'my_simulink_model4'
eng.new_system(model_name, nargout=0)
eng.open_system(model_name, nargout=0)
interf.input_system(eng, model_name)