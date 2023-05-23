
from components import *
from system import *
from model_builder import *
from interface import *
from abstract_factory import *
import matlab
import matlab.engine
from upgrader import *
#%%
f = DCBuilder()
f.build_system(seed=5)
sys = f.product()
# interf = SystemSimulinkAdapter(sys)
# eng = matlab.engine.start_matlab()
# model_name = 'my_simulink_model4'
# eng.new_system(model_name, nargout=0)
# eng.open_system(model_name, nargout=0)
# interf.input_system(eng, model_name)
#%%
# sensor_subsys_group = {}
# for subsys in sys.subsystem_list:
#     if 'sensor' in subsys.subsystem_type:
#         sensor_group = {}
#         for component in subsys.component_list:
#             if component.component_type == 'Sensor':
#                 if component.name in sensor_group:
#                     sensor_group[component.name].append(component)
#                 else:
#                     sensor_group[component.name] = [component]
#         sensor_subsys_group[f'{subsys.subsystem_type}_{subsys.ID}'] = sensor_group

#%%
# def create_upgrade_component(name, categary):
#     component_factory = ElectriaclComponentFactory()
#     comp = component_factory.create_component(name, categary, randomattr=False)
#     comp.name = comp.name + 'Upgrade'
#     return comp
# keys = list(sensor_subsys_group.keys())
# subsys_key = random.choice(keys)
# sensor_group = sensor_subsys_group[subsys_key]
# key = subsys_key.rsplit('_', 1)
#%%
# for subsys in sys.subsystem_list:
#     num_to_workspace = 0
#     if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
#         for name, sensors_list in sensor_group.items():
#             if name == 'CurrentSensor':
#                 logic = create_upgrade_component('Comparator', Logic)
#                 to_workspace = create_upgrade_component('ToWorkspace', Workspace)
#                 to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
#                 num_to_workspace += 1
#                 subsys.add_component(logic, to_workspace)
#                 subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
#                 length = len(sensors_list)
#                 cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
#                 if length < 2:
#                     sensor = create_upgrade_component(name, ElectricalSensor)
#                     subsys.add_component(sensor)
#                     old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
#                     for connection in old_connect[0]:
#                         remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
#                         subsys.connections.remove(connection)
#                         subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
#                     subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
#                                            cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
#                     sensor_new_list = [sensor, cunrrent_sensors[0]]
#                 else:
#                     sensor_new_list = random.sample(cunrrent_sensors, 2)
#                 for i, new_sensor in enumerate(sensor_new_list):
#                     port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
#                     converter = create_upgrade_component('PSSimuConv', Utilities)
#                     subsys.add_component(converter)
#                     subsys.add_connection((converter.get_port_info()[-1], logic.get_port_info()[i]))
#                     subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#             if name == 'VoltageSensor':
#                 logic = create_upgrade_component('Comparator', Logic)
#                 to_workspace = create_upgrade_component('ToWorkspace', Workspace)
#                 to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
#                 num_to_workspace += 1
#                 subsys.add_component(logic, to_workspace)
#                 subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
#                 length = len(sensors_list)
#                 voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
#                 if length < 2:
#                     sensor = create_upgrade_component(name, ElectricalSensor)
#                     subsys.add_component(sensor)
#                     old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
#                                                              voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
#                     for i, connections in enumerate(old_connect):
#                         for connection in connections:
#                             remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(i+1)].replace('+', '').replace('-', '')]
#                             subsys.add_connection((sensor.get_port_info()[-(i+1)].replace('+', '').replace('-', ''), remain_port[0]))
#                     sensor_new_list = [sensor, voltage_sensors[0]]
#                 else:
#                     sensor_new_list = random.sample(voltage_sensors, 2)
#                 for i, new_sensor in enumerate(sensor_new_list):
#                     port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
#                     converter = create_upgrade_component('PSSimuConv', Utilities)
#                     subsys.add_component(converter)
#                     subsys.add_connection((converter.get_port_info()[-1], logic.get_port_info()[i]))
#                     subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
# odd_integer = random.randrange(3, 6, 2)
# for subsys in sys.subsystem_list:
#     num_to_workspace = 0
#     if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
#         for name, sensors_list in sensor_group.items():
#             if name == 'CurrentSensor':
#                 logic = create_upgrade_component('Voter', Logic)
#                 mux = create_upgrade_component('Mux', Logic)
#                 mux.set_input(odd_integer)
#                 to_workspace = create_upgrade_component('ToWorkspace', Workspace)
#                 to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
#                 num_to_workspace += 1
#                 subsys.add_component(logic, mux, to_workspace)
#                 subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
#                 subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
#                 length = len(sensors_list)
#                 cunrrent_sensors = [comp for comp in subsys.component_list if comp.name == 'CurrentSensor']
#                 if length < odd_integer:
#                     for i in range(odd_integer - length):
#                         sensor = create_upgrade_component(name, ElectricalSensor)
#                         subsys.add_component(sensor)
#                         old_connect = subsys.filter_connections([cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
#                         for connection in old_connect[0]:
#                             remain_port = [x for x in connection if x != cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')]
#                             subsys.connections.remove(connection)
#                             subsys.add_connection((sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
#                         subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
#                                                cunrrent_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')))
#                         cunrrent_sensors.append(sensor)
#                     sensor_new_list = cunrrent_sensors
#                 else:
#                     sensor_new_list = random.sample(cunrrent_sensors, odd_integer)
#                 for i, new_sensor in enumerate(sensor_new_list):
#                     port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
#                     converter = create_upgrade_component('PSSimuConv', Utilities)
#                     subsys.add_component(converter)
#                     subsys.add_connection((converter.get_port_info()[-1], mux.get_port_info()[i]))
#                     subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#             if name == 'VoltageSensor':
#                 logic = create_upgrade_component('Voter', Logic)
#                 mux = create_upgrade_component('Mux', Logic)
#                 mux.set_input(odd_integer)
#                 to_workspace = create_upgrade_component('ToWorkspace', Workspace)
#                 to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
#                 num_to_workspace += 1
#                 subsys.add_component(logic, mux, to_workspace)
#                 subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
#                 subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
#                 length = len(sensors_list)
#                 voltage_sensors = [comp for comp in subsys.component_list if comp.name == 'VoltageSensor']
#                 if length < odd_integer:
#                     for i in range(odd_integer - length):
#                         sensor = create_upgrade_component(name, ElectricalSensor)
#                         subsys.add_component(sensor)
#                         old_connect = subsys.filter_connections([voltage_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
#                                                                  voltage_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
#                         for n, connections in enumerate(old_connect):
#                             for connection in connections:
#                                 remain_port = [x for x in connection if x != voltage_sensors[0].get_port_info()[-(n+1)].replace('+', '').replace('-', '')]
#                                 subsys.add_connection((sensor.get_port_info()[-(n+1)].replace('+', '').replace('-', ''), remain_port[0]))
#                         voltage_sensors.append(sensor)
#                     sensor_new_list = voltage_sensors
#                 else:
#                     sensor_new_list = random.sample(voltage_sensors, odd_integer)
#                 for i, new_sensor in enumerate(sensor_new_list):
#                     port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
#                     converter = create_upgrade_component('PSSimuConv', Utilities)
#                     subsys.add_component(converter)
#                     subsys.add_connection((converter.get_port_info()[-1], mux.get_port_info()[i]))
#                     subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
#%%
up = BasicUpgrader(sys)
#%%
sigup = SingleUpgrader(up)
sigup.upgrade(subsystem_type='sensor_current', subsystem_id=0, target=3)
#%%
# sigup.upgrade(subsystem_type= 'sensor_both', subsystem_id=0, target=2)
#%%
comup = CombineUpgrader(up)
#%%
# comup.upgrade(subsystem_type= 'sensor_current', subsystem_id=0, target=4)
#%%
comup.upgrade(pattern_name= 'C+V', subsystem_type='sensor_voltage', subsystem_id=0, target=2)
#%%
interf = SystemSimulinkAdapter(sys)
eng = matlab.engine.start_matlab()
model_name = 'my_simulink_model5'
eng.new_system(model_name, nargout=0)
eng.open_system(model_name, nargout=0)
interf.input_system(eng, model_name)




