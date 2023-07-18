from components import *
from system import *
from model_builder import *
from interface import *
from abstract_factory import *
import matlab
import matlab.engine
import copy
class Upgrader():
    def upgrade(self):
        pass


# Concrete Component
class BasicUpgrader(Upgrader):
    def __init__(self, system):
        self.origin_sys = copy.deepcopy(system)
        self.sys = system

    def upgrade(self):
        return self.sys

class UpgraderDecorator(Upgrader):
    def __init__(self, upgrader):
        self.wrappee = upgrader

    def upgrade(self):
        self.wrappee.upgrade()

    def create_upgrade_component(self, name, categary):
        component_factory = ElectriaclComponentFactory()
        comp = component_factory.create_component(name, categary, randomattr=False)
        comp.name = comp.name + 'Upgrade'
        return comp

    def add_current_sensor(self, sensor, old_sensors, subsys):
        old_connect = subsys.filter_connections(
            [old_sensors[0].get_port_info()[-1].replace('+', '').replace('-', '')])
        for connection in old_connect[0]:
            remain_port = [x for x in connection if
                           x != old_sensors[0].get_port_info()[-1].replace('+', '').replace(
                               '-', '')]
            subsys.connections.remove(connection)
            subsys.add_connection(
                (sensor.get_port_info()[-1].replace('+', '').replace('-', ''), remain_port[0]))
        subsys.add_connection((sensor.get_port_info()[1].replace('+', '').replace('-', ''),
                               old_sensors[0].get_port_info()[-1].replace('+', '').replace('-',
                                                                                                '')))
    def add_voltage_sensor(self, sensor, old_sensors, subsys):
        old_connect = subsys.filter_connections(
            [old_sensors[0].get_port_info()[-1].replace('+', '').replace('-', ''),
             old_sensors[0].get_port_info()[-2].replace('+', '').replace('-', '')])
        for i, connections in enumerate(old_connect):
            for connection in connections:
                remain_port = [x for x in connection if
                               x != old_sensors[0].get_port_info()[-(i + 1)].replace('+',
                                                                                         '').replace(
                                   '-', '')]
                subsys.add_connection((
                    sensor.get_port_info()[-(i + 1)].replace('+', '').replace('-',
                                                                              ''),
                    remain_port[0]))

    def restore_subsys(self, subsys_type, subsys_id):
        subsys_id = int(subsys_id)
        for i, subsys in enumerate(self.wrappee.sys.subsystem_list):
            if subsys.subsystem_type == subsys_type and subsys.ID == subsys_id:
                for comp in subsys.component_list:
                    if 'Upgrade' in comp.name:
                        for subsys_2 in self.wrappee.origin_sys.subsystem_list:
                            if subsys_2.subsystem_type == subsys_type and subsys_2.ID == subsys_id:
                                self.wrappee.sys.subsystem_list[i] = copy.deepcopy(subsys_2)
                                break
                        break
    def check_sensor_signal(self, subsys, sensor_name, sensor_id):
        check = 0
        sensor_key = f'{sensor_name}_id{sensor_id}'
        ports = [t[1] if sensor_key in t[0] else t[0] for t in
                 subsys.connections if sensor_key in t[0] or sensor_key in t[1]]
        for port in ports:
            if 'PSSimuConv' in port:
                convert = port
            if 'PSSimuConvUpgrade' in port:
                convert = port
                break
        check_ports = [t[1] if t[0] == convert else t[0] for t in
                       subsys.connections if t[0] == convert or t[1] == convert]
        for p in check_ports:
            if 'SignalAlter' in p:
                check = 1
        return convert, check
    def alter_sensor_signal(self, subsystem_type=None, subsystem_id=None, sensor_name=None, sensor_id=None, seed=None):
        if seed:
            random.seed(seed)
        if subsystem_type is None or subsystem_id is None:
            sensor_subs = []
            for i, subsys in enumerate(self.wrappee.sys.subsystem_list):
                if 'sensor' in subsys.subsystem_type:
                    p1 = 0
                    p2 = 0
                    for comp in subsys.component_list:
                        if 'SignalAlter' in comp.name:
                            p1 += 1
                        if 'Sensor' in comp.name:
                            p2 += 1
                    if p2 > p1:
                        sensor_subs.append(subsys)
            if not sensor_subs:
                raise ValueError(f'There is no available sensor systems')
            subsys = random.choice(sensor_subs)
            subsystem_type = subsys.subsystem_type
            subsystem_id = subsys.ID
        for i, subsys in enumerate(self.wrappee.sys.subsystem_list):
            if subsys.subsystem_type == subsystem_type and subsys.ID == subsystem_id:
                sensors = []
                if sensor_name is None or sensor_id is None:
                    for comp in subsys.component_list:
                        if 'Sensor' in comp.name:
                            sensors.append(comp)
                    sensor = random.choice(sensors)
                    sensor_name = sensor.name
                    sensor_id = sensor.ID
                    convert, check = self.check_sensor_signal(subsys, sensor_name, sensor_id)
                    while check:
                        sensor = random.choice(sensors)
                        sensor_name = sensor.name
                        sensor_id = sensor.ID
                        convert, check = self.check_sensor_signal(subsys, sensor_name, sensor_id)
                else:
                    convert, check = self.check_sensor_signal(subsys, sensor_name, sensor_id)
                id_index = convert.find('id')
                underscore_index = convert.find('_', id_index)
                connect_port = convert[:underscore_index]
                connect_port = f'{connect_port}_portOUT1'
                alter = self.create_upgrade_component('SignalAlter', Logic)
                subsys.add_component(alter)
                new_connnection_list = []
                for t in subsys.connections:
                    new_t = tuple(alter.get_port_info()[-1] if i == connect_port else i for i in t)
                    new_connnection_list.append(new_t)
                subsys.connections = new_connnection_list
                subsys.add_connection((alter.get_port_info()[0], connect_port))
    def relpace_component(self, new_component_name, new_component_class, subsystem_type, subsystem_id, component_name, component_id):
        for i, subsys in enumerate(self.wrappee.sys.subsystem_list):
            if subsys.subsystem_type == subsystem_type and subsys.ID == subsystem_id:
                new_component = self.create_upgrade_component(new_component_name, new_component_class)
                for comp in subsys.component_list:
                    if comp.name == component_name and comp.ID == component_id:
                        if comp.port == new_component.port:
                            subsys.add_component(new_component)
                            new_connnection_list = []
                            key = f'{component_name}_id{component_id}'
                            new_key = f'{new_component.name}_id{new_component.ID}'
                            for connection in subsys.connections:
                                new_connection = tuple(p.replace(key, new_key) if key in p else p for p in connection)
                                new_connnection_list.append(new_connection)
                            subsys.connections = new_connnection_list
                            subsys.component_list.remove(comp)
                        else:
                            raise ValueError(f'ports are not same between the two components')


class SingleUpgrader(UpgraderDecorator):
    def comparator_pattern(self, key, sensor_group):
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        logic = self.create_upgrade_component('Comparator', Logic)
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(logic, to_workspace)
                        subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < 2:
                            sensor = self.create_upgrade_component(name, ElectricalSensor)
                            subsys.add_component(sensor)
                            if name == 'CurrentSensor':
                                self.add_current_sensor(sensor, old_sensors, subsys)
                            if name == 'VoltageSensor':
                                self.add_voltage_sensor(sensor, old_sensors, subsys)
                            sensor_new_list = [sensor, old_sensors[0]]
                        else:
                            sensor_new_list = random.sample(old_sensors, 2)
                        for i, new_sensor in enumerate(sensor_new_list):
                            port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                            converter = self.create_upgrade_component('PSSimuConv', Utilities)
                            subsys.add_component(converter)
                            subsys.add_connection((converter.get_port_info()[-1], logic.get_port_info()[i]))
                            subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))

    def voter_pattern(self, key, sensor_group, target):
        if target:
            if not isinstance(target, int):
                if target % 1 > 0:
                    target += 1
                target = int(target)
            odd_integer = 2 * target + 1
        else:
            odd_integer = random.randrange(3, 6, 2)
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        logic = self.create_upgrade_component('Voter', Logic)
                        mux = self.create_upgrade_component('Mux', Utilities)
                        mux.set_input(odd_integer)
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(logic, mux, to_workspace)
                        subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < odd_integer:
                            for i in range(odd_integer - length):
                                sensor = self.create_upgrade_component(name, ElectricalSensor)
                                subsys.add_component(sensor)
                                if name == 'CurrentSensor':
                                    self.add_current_sensor(sensor, old_sensors, subsys)
                                if name == 'VoltageSensor':
                                    self.add_voltage_sensor(sensor, old_sensors, subsys)
                                old_sensors.append(sensor)
                            sensor_new_list = old_sensors
                        else:
                            sensor_new_list = random.sample(old_sensors, odd_integer)
                        for i, new_sensor in enumerate(sensor_new_list):
                            port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                            converter = self.create_upgrade_component('PSSimuConv', Utilities)
                            subsys.add_component(converter)
                            subsys.add_connection((converter.get_port_info()[-1], mux.get_port_info()[i]))
                            subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
                subsys.fault_tolerant = (odd_integer - 1)/2

    def upgrade(self, pattern_name=None, subsystem_type=None, subsystem_id=None, target=None, seed=None):
        if seed:
            random.seed(seed)
        sensor_subsys_group = {}
        for subsys in self.wrappee.sys.subsystem_list:
            if 'sensor' in subsys.subsystem_type:
                sensor_group = {}
                for component in subsys.component_list:
                    if component.component_type == 'Sensor':
                        if component.name in sensor_group:
                            sensor_group[component.name].append(component)
                        else:
                            sensor_group[component.name] = [component]
                sensor_subsys_group[f'{subsys.subsystem_type}_{subsys.ID}'] = sensor_group
        if subsystem_type and subsystem_id is not None:
            key = [None]*2
            key[0] = subsystem_type
            key[1] = subsystem_id
            sensor_group = sensor_subsys_group[f'{subsystem_type}_{subsystem_id}']
        else:
            keys = list(sensor_subsys_group.keys())
            subsys_key = random.choice(keys)
            sensor_group = sensor_subsys_group[subsys_key]
            key = subsys_key.rsplit('_', 1)
        if pattern_name is None:
            if target is None:
                pattern_name = random.choice(['comparator', 'voter'])
            else:
                pattern_name = 'voter'
        self.restore_subsys(key[0], key[1])
        if pattern_name == 'comparator':
            self.comparator_pattern(key, sensor_group)
        elif pattern_name == 'voter':
            self.voter_pattern(key, sensor_group, target)
        else:
            raise ValueError(f"{pattern_name} is not a valid single pattern name.")


class CombineUpgrader(UpgraderDecorator):
    def c_and_v_pattern(self, key, sensor_group, target):
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                if target:
                    if not isinstance(target, int):
                        if target % 1 > 0:
                            target += 1
                        target = int(target)
                    odd_integer = target + 1
                    if odd_integer % 2 == 0:
                        odd_integer += 1
                else:
                    odd_integer = random.randrange(3, 4, 2)
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        logic = self.create_upgrade_component('Voter', Logic)
                        mux = self.create_upgrade_component('Mux', Utilities)
                        mux.set_input(odd_integer)
                        signal = self.create_upgrade_component('Constant', Signal)
                        signal.value = 'nan'
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(logic, mux, to_workspace, signal)
                        subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < odd_integer * 2:
                            for i in range(odd_integer * 2 - length):
                                sensor = self.create_upgrade_component(name, ElectricalSensor)
                                subsys.add_component(sensor)
                                if name == 'CurrentSensor':
                                    self.add_current_sensor(sensor, old_sensors, subsys)
                                if name == 'VoltageSensor':
                                    self.add_voltage_sensor(sensor, old_sensors, subsys)
                                old_sensors.append(sensor)
                            sensor_new_list = old_sensors
                        else:
                            sensor_new_list = random.sample(old_sensors, odd_integer * 2)
                        new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in
                                    range(0, len(sensor_new_list), 2)]
                        for i, new_pair in enumerate(new_list):
                            comparator = self.create_upgrade_component('Comparator', Logic)
                            switch = self.create_upgrade_component('CommonSwitch', Utilities)
                            subsys.add_component(comparator, switch)
                            subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                            subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                            subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                            for n, new_sensor in enumerate(new_pair):
                                port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                                converter = self.create_upgrade_component('PSSimuConv', Utilities)
                                subsys.add_component(converter)
                                if n == 0:
                                    subsys.add_connection(
                                        (converter.get_port_info()[-1], switch.get_port_info()[0]))
                                subsys.add_connection(
                                    (converter.get_port_info()[-1], comparator.get_port_info()[n]))
                                subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
                subsys.fault_tolerant = odd_integer - 1
    def v_and_c_pattern(self, key, sensor_group, target):
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                if target:
                    if not isinstance(target, int):
                        if target % 1 > 0:
                            target += 1
                        target = int(target)
                    odd_integer = target + 2
                    if odd_integer % 2 == 0:
                        odd_integer += 1
                else:
                    odd_integer = random.randrange(3, 4, 2)
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        logic = self.create_upgrade_component('Voter', Logic)
                        mux = self.create_upgrade_component('Mux', Utilities)
                        delay_out = self.create_upgrade_component('UnitDelay', Utilities)
                        mux.set_input(odd_integer)
                        signal = self.create_upgrade_component('Constant', Signal)
                        signal.value = 'nan'
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(logic, mux, to_workspace, signal, delay_out)
                        subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        subsys.add_connection((logic.get_port_info()[-1], delay_out.get_port_info()[0]))
                        subsys.add_connection((logic.get_port_info()[0], mux.get_port_info()[-1]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < odd_integer:
                            for i in range(odd_integer - length):
                                sensor = self.create_upgrade_component(name, ElectricalSensor)
                                subsys.add_component(sensor)
                                if name == 'CurrentSensor':
                                    self.add_current_sensor(sensor, old_sensors, subsys)
                                if name == 'VoltageSensor':
                                    self.add_voltage_sensor(sensor, old_sensors, subsys)
                                old_sensors.append(sensor)
                            sensor_new_list = old_sensors
                        else:
                            sensor_new_list = random.sample(old_sensors, odd_integer)
                        for i, new_sensor in enumerate(sensor_new_list):
                            comparator = self.create_upgrade_component('Comparator', Logic)
                            switch = self.create_upgrade_component('CommonSwitch', Utilities)
                            delay = self.create_upgrade_component('UnitDelay', Utilities)
                            subsys.add_component(comparator, switch, delay)
                            subsys.add_connection((comparator.get_port_info()[-1], switch.get_port_info()[1]))
                            subsys.add_connection((signal.get_port_info()[-1], switch.get_port_info()[2]))
                            subsys.add_connection((switch.get_port_info()[-1], mux.get_port_info()[i]))
                            port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                            converter = self.create_upgrade_component('PSSimuConv', Utilities)
                            subsys.add_component(converter)
                            subsys.add_connection((converter.get_port_info()[-1], switch.get_port_info()[0]))
                            subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                            subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                            subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                            subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
                subsys.fault_tolerant = odd_integer - 2
    def c_and_s_pattern(self, key, sensor_group):
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                even_integer = random.randrange(4, 7, 2)
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        logic = self.create_upgrade_component('Sparing', Logic)
                        mux_signal = self.create_upgrade_component('Mux', Utilities)
                        mux = self.create_upgrade_component('Mux', Utilities)
                        mux_signal.set_input(int(even_integer / 2))
                        mux.set_input(int(even_integer / 2))
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(logic, mux_signal, mux, to_workspace)
                        subsys.add_connection((logic.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        subsys.add_connection((logic.get_port_info()[0], mux_signal.get_port_info()[-1]))
                        subsys.add_connection((logic.get_port_info()[1], mux.get_port_info()[-1]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < even_integer:
                            for i in range(even_integer - length):
                                sensor = self.create_upgrade_component(name, ElectricalSensor)
                                subsys.add_component(sensor)
                                if name == 'CurrentSensor':
                                    self.add_current_sensor(sensor, old_sensors, subsys)
                                if name == 'VoltageSensor':
                                    self.add_voltage_sensor(sensor, old_sensors, subsys)
                                old_sensors.append(sensor)
                            sensor_new_list = old_sensors
                        else:
                            sensor_new_list = random.sample(old_sensors, even_integer)
                        new_list = [[sensor_new_list[i], sensor_new_list[i + 1]] for i in
                                    range(0, len(sensor_new_list), 2)]
                        for i, new_pair in enumerate(new_list):
                            comparator = self.create_upgrade_component('Comparator', Logic)
                            subsys.add_component(comparator)
                            subsys.add_connection((comparator.get_port_info()[-1], mux.get_port_info()[i]))
                            for n, new_sensor in enumerate(new_pair):
                                port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                                converter = self.create_upgrade_component('PSSimuConv', Utilities)
                                subsys.add_component(converter)
                                if n == 0:
                                    subsys.add_connection(
                                        (converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                                subsys.add_connection(
                                    (converter.get_port_info()[-1], comparator.get_port_info()[n]))
                                subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
    def v_and_c_and_s_pattern(self, key, sensor_group, target):
        for subsys in self.wrappee.sys.subsystem_list:
            num_to_workspace = 0
            if subsys.subsystem_type == key[0] and subsys.ID == int(key[1]):
                if target:
                    if not isinstance(target, int):
                        if target % 1 > 0:
                            target += 1
                        target = int(target)
                    num_integer = target + 2
                else:
                    num_integer = random.randrange(3, 5, 1)
                odd_integer = random.randrange(3, num_integer + 1, 2)
                for name, sensors_list in sensor_group.items():
                    if name == 'CurrentSensor' or name == 'VoltageSensor':
                        voter = self.create_upgrade_component('Voter', Logic)
                        spare = self.create_upgrade_component('Sparing', Logic)
                        spare.n = odd_integer
                        mux_signal = self.create_upgrade_component('Mux', Utilities)
                        mux_error = self.create_upgrade_component('Mux', Utilities)
                        mux_signal.set_input(num_integer)
                        mux_error.set_input(num_integer)
                        delay_out = self.create_upgrade_component('UnitDelay', Utilities)
                        to_workspace = self.create_upgrade_component('ToWorkspace', Workspace)
                        to_workspace.variable_name = f'{subsys.subsystem_type}_{subsys.ID}_upgrade_{num_to_workspace}'
                        num_to_workspace += 1
                        subsys.add_component(voter, spare, mux_signal, mux_error, to_workspace,
                                             delay_out)
                        subsys.add_connection((voter.get_port_info()[-1], to_workspace.get_port_info()[0]))
                        subsys.add_connection((voter.get_port_info()[-1], delay_out.get_port_info()[0]))
                        subsys.add_connection((voter.get_port_info()[0], spare.get_port_info()[-1]))
                        subsys.add_connection((mux_signal.get_port_info()[-1], spare.get_port_info()[0]))
                        subsys.add_connection((mux_error.get_port_info()[-1], spare.get_port_info()[1]))
                        length = len(sensors_list)
                        old_sensors = [comp for comp in subsys.component_list if comp.name == name]
                        if length < num_integer:
                            for i in range(num_integer - length):
                                sensor = self.create_upgrade_component(name, ElectricalSensor)
                                subsys.add_component(sensor)
                                if name == 'CurrentSensor':
                                    self.add_current_sensor(sensor, old_sensors, subsys)
                                if name == 'VoltageSensor':
                                    self.add_voltage_sensor(sensor, old_sensors, subsys)
                                old_sensors.append(sensor)
                            sensor_new_list = old_sensors
                        else:
                            sensor_new_list = random.sample(old_sensors, num_integer)
                        for i, new_sensor in enumerate(sensor_new_list):
                            comparator = self.create_upgrade_component('Comparator', Logic)
                            delay = self.create_upgrade_component('UnitDelay', Utilities)
                            subsys.add_component(comparator, delay)
                            subsys.add_connection((comparator.get_port_info()[-1], mux_error.get_port_info()[i]))
                            port = [elem for elem in new_sensor.get_port_info() if 'scope' in elem]
                            converter = self.create_upgrade_component('PSSimuConv', Utilities)
                            subsys.add_component(converter)
                            subsys.add_connection((converter.get_port_info()[-1], mux_signal.get_port_info()[i]))
                            subsys.add_connection((converter.get_port_info()[-1], delay.get_port_info()[0]))
                            subsys.add_connection((delay.get_port_info()[-1], comparator.get_port_info()[0]))
                            subsys.add_connection((delay_out.get_port_info()[-1], comparator.get_port_info()[1]))
                            subsys.add_connection((converter.get_port_info()[0], port[0].replace('scope', '')))
                subsys.fault_tolerant = num_integer - 2
    def upgrade(self, pattern_name=None, subsystem_type=None, subsystem_id=None, target=None, seed=None):
        if seed:
            random.seed(seed)
        sensor_subsys_group = {}
        for subsys in self.wrappee.sys.subsystem_list:
            if 'sensor' in subsys.subsystem_type:
                sensor_group = {}
                for component in subsys.component_list:
                    if component.component_type == 'Sensor':
                        if component.name in sensor_group:
                            sensor_group[component.name].append(component)
                        else:
                            sensor_group[component.name] = [component]
                sensor_subsys_group[f'{subsys.subsystem_type}_{subsys.ID}'] = sensor_group
        if subsystem_type and subsystem_id is not None:
            key = [None]*2
            key[0] = subsystem_type
            key[1] = subsystem_id
            sensor_group = sensor_subsys_group[f'{subsystem_type}_{subsystem_id}']
        else:
            keys = list(sensor_subsys_group.keys())
            subsys_key = random.choice(keys)
            sensor_group = sensor_subsys_group[subsys_key]
            key = subsys_key.rsplit('_', 1)
        if pattern_name is None:
            if target is None:
                pattern_name = random.choice(['C+V', 'V+C', 'C+S', 'V+C+S'])
            else:
                pattern_name = random.choice(['V+C', 'V+C+S'])
        self.restore_subsys(key[0], key[1])
        print(pattern_name)
        if pattern_name == 'C+V':
            self.c_and_v_pattern(key, sensor_group, target)
        elif pattern_name == 'V+C':
            self.v_and_c_pattern(key, sensor_group, target)
        elif pattern_name == 'C+S':
            self.c_and_s_pattern(key, sensor_group)
        elif pattern_name == 'V+C+S':
            self.v_and_c_and_s_pattern(key, sensor_group, target)
        else:
            raise ValueError(f"{pattern_name} is not a valid pattern name.")


