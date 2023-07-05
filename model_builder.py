import random
import gin
from system import System, Subsystem
from abstract_factory import *


class ModelBuilder:
    def __init__(self, component_factory):
        self.component_factory = component_factory

    def build_system(self):
        pass

    def product(self):
        pass


class ElectricalModelBuilder(ModelBuilder):
    def __init__(self, component_factory):
        super().__init__(component_factory)

    def build_system(self):
        pass

    def product(self):
        pass

@gin.configurable
class ACBuilder(ElectricalModelBuilder):
    def __init__(self):
        super().__init__(ACComponentFactory())
        self.reset()

    def reset(self):
        self._model = System()

    def product(self):
        model = self._model
        return model

    def series_connect(self, subsys, component, inport, outport):
        subsystem = subsys
        comp = component
        in_port = inport
        out_port = outport
        comp_port = [obj.get_port_info() for obj in comp]
        if len(comp_port) == 1:
            list_first = [elem for elem in comp_port[0] if '+' in elem]
            subsystem.add_connection((list_first[0].replace('+', ''), in_port[0].get_port_info()[0]))
            list_last = [elem for elem in comp_port[0] if '-' in elem]
            subsystem.add_connection((list_last[0].replace('-', ''), out_port[0].get_port_info()[0]))
        else:
            for i in range(len(comp_port) - 1):
                list_negative = [elem for elem in comp_port[i] if '-' in elem]
                list_positive = [elem for elem in comp_port[i + 1] if '+' in elem]
                if i == 0:
                    list_first = [elem for elem in comp_port[i] if '+' in elem]
                    subsystem.add_connection((list_first[0].replace('+', ''), in_port[0].get_port_info()[0]))
                if i == len(comp_port) - 2:
                    list_last = [elem for elem in comp_port[i+1] if '-' in elem]
                    subsystem.add_connection((list_last[0].replace('-', ''), out_port[0].get_port_info()[0]))
                new_connect = (list_positive[0].replace('+', ''), list_negative[0].replace('-', ''))
                subsystem.add_connection(new_connect)
        return subsystem

    def parallel_connect(self, subsys, component, inport, outport):
        subsystem = subsys
        comp = component
        in_port = inport
        out_port = outport
        for comp in comp:
            for port in comp.get_port_info():
                if '+' in port:
                    subsystem.add_connection((port.replace('+', ''), in_port[0].get_port_info()[0]))
                if '-' in port:
                    subsystem.add_connection((port.replace('-', ''), out_port[0].get_port_info()[0]))
        return subsystem

    def create_source_subsystem(self, type, max_num_component=3, seed=None, battery_exsist=None):
        if seed:
            random.seed(seed)
        if type == 'voltage':
            subsystem = Subsystem(subsystem_type='source_voltage')
            num_sources = random.randint(1, max_num_component)
            for i in range(num_sources):
                if battery_exsist:
                    type = random.choice(['voltage', 'battery'])
                    component = self.component_factory.create_source(type=type, seed=seed)
                else:
                    component = self.component_factory.create_source(type='voltage', seed=seed)
                subsystem.add_component(component)
            #connent to signal
            comp = [comp for comp in subsystem.component_list if comp.component_type == 'Source']
            comp_port = [obj.get_port_info() for obj in comp]
            list_signal = []
            for i in range(len(comp_port)):
                list = [elem for elem in comp_port[i] if 'signal' in elem]
                list_signal.extend(list)
            if list_signal:
                for i in range(len(list_signal)):
                    from_workspace = self.component_factory.create_workspace('FromWorkspace')
                    converter = self.component_factory.create_utilities('SimuPSConv')
                    subsystem.add_component(from_workspace, converter)
                from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
                converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
                index_sig = 0
                for port in list_signal:
                        subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1]),
                                                 (converter[index_sig].get_port_info()[0], from_workspace[index_sig].get_port_info()[0]))
                        index_sig += 1
            # connect with ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem_connected = self.series_connect(subsystem, comp, in_port, out_port)
        if type == 'current':
            subsystem = Subsystem(subsystem_type='source_current')
            num_sources = random.randint(1, max_num_component)
            for i in range(num_sources):
                component = self.component_factory.create_source(type='current', seed=seed)
                subsystem.add_component(component)
            #connent to signal
            comp = [comp for comp in subsystem.component_list if comp.component_type == 'Source']
            comp_port = [obj.get_port_info() for obj in comp]
            list_signal = []
            for i in range(len(comp_port)):
                list = [elem for elem in comp_port[i] if 'signal' in elem]
                list_signal.extend(list)
            if list_signal:
                for i in range(len(list_signal)):
                    from_workspace = self.component_factory.create_workspace('FromWorkspace')
                    converter = self.component_factory.create_utilities('SimuPSConv')
                    subsystem.add_component(from_workspace, converter)
                from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
                converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
                index_sig = 0
                for port in list_signal:
                        subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                                 , (converter[index_sig].get_port_info()[0],
                                                    from_workspace[index_sig].get_port_info()[0]))
                        index_sig += 1
            # connect with ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem_connected = self.parallel_connect(subsystem, comp, in_port, out_port)
        subsystem_connected.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem_connected.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem_connected

    def create_element_subsystem(self, max_num_component=5, seed=None):
        subsystem = Subsystem(subsystem_type='element')
        if seed:
            random.seed(seed)
        #create elements randomly
        num_components = random.randint(1, max_num_component)
        for i in range(num_components):
            component = self.component_factory.create_element(seed=seed)
            subsystem.add_component(component)
        #connect signal port
        comp = [comp for comp in subsystem.component_list if comp.component_type == 'Element']
        comp_port = [obj.get_port_info() for obj in comp]
        list_signal = []
        for element in comp:
            for one_port in element.port:
                if 'signal' in one_port:
                    element.port.remove(one_port)
        for i in range(len(comp_port)):
            list = [elem for elem in comp_port[i] if 'signal' in elem]
            list_signal.extend(list)
        if list_signal:
            for i in range(len(list_signal)):
                from_workspace = self.component_factory.create_workspace('FromWorkspace')
                converter = self.component_factory.create_utilities('SimuPSConv')
                subsystem.add_component(from_workspace, converter)
            from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
            converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
            index_sig = 0
            for port in list_signal:
                subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                         , (converter[index_sig].get_port_info()[0],
                                            from_workspace[index_sig].get_port_info()[0]))
                index_sig += 1
        #connect component
        group = [element for element in subsystem.component_list if element.component_type == 'Element']
        chosen_pair = []
        first_component = random.choice(group)
        all_ports = first_component.get_port_info()
        group.remove(first_component)
        connected_components = [first_component]
        while group:
            component = random.choice(group)
            new_ports = component.get_port_info()
            all_ports.extend(new_ports)
            port_pairs = []
            for c in connected_components:
                # generate all possible port pairs between the new component and the connected components
                connected_ports = c.get_port_info()
                for np in new_ports:
                    for cp in connected_ports:
                        port_pairs.append((np, cp))
            # choose a random port pair and connect the components
            port_pair = random.choice(port_pairs)
            chosen_pair.append(port_pair)
            subsystem.add_connection(port_pair)
            connected_components.append(component)
            group.remove(component)
        #find out unused ports
        unused_port = [port for port in all_ports if
                          port not in [pair[0] for pair in chosen_pair] and port not in
                          [pair[1] for pair in chosen_pair]]
        #add input and output for subsystem
        inport = self.component_factory.create_port('Inport', type='electrical')
        outport = self.component_factory.create_port('Outport', type='electrical')
        subsystem.add_component(inport,outport)
        n = random.randint(0, len(unused_port)-2)
        for i in range(n):
            port_name = random.choice(['Inport','Outport'])
            port = self.component_factory.create_port(port_name, type='electrical')
            subsystem.add_component(port)
        #connect components with input and output
        subsystem_port = [port_class for port_class in subsystem.component_list if port_class.component_type == 'Port']
        in_out_ports = []
        for port in subsystem_port:
            in_out_ports.extend(port.get_port_info())
        in_out_ports_copy = in_out_ports.copy()
        for item2 in unused_port:
            if len(in_out_ports_copy) == 0:
                in_out_ports_copy = in_out_ports.copy()
            item1 = random.choice(in_out_ports_copy)
            subsystem.add_connection((item1, item2))
            in_out_ports_copy.remove(item1)
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_actuator_subsystem(self, seed=None, pole_and_throw=None):
        subsystem = Subsystem(subsystem_type='switch')
        if seed:
            random.seed(seed)
        component = self.component_factory.create_actuator(seed=seed, pole_and_throw=pole_and_throw)
        subsystem.add_component(component)
        switchs = [switch for switch in subsystem.component_list if switch.component_type == 'Actuator']
        for switch in switchs:
            for i in range(len(switch.take_port('LConn')) - 1):
                inport = self.component_factory.create_port('Inport', type='electrical')
                subsystem.add_component(inport)
            for i in range(len(switch.take_port('RConn'))):
                outport = self.component_factory.create_port('Outport', type='electrical')
                subsystem.add_component(outport)
            from_workspace = self.component_factory.create_workspace('FromWorkspace')
            converter = self.component_factory.create_utilities('SimuPSConv')
            subsystem.add_component(from_workspace, converter)
        #connect with port
        in_port = [port_class for port_class in subsystem.component_list if
                   port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if
                    port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
        converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
        index_sig = 0
        index_in = 0
        index_out = 0
        for switch in switchs:
            for port in switch.get_port_info():
                if 'signal' in port:
                    subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                             ,(converter[index_sig].get_port_info()[0],from_workspace[index_sig].get_port_info()[0]))
                    index_sig += 1
                if 'LConn' in port and 'signal' not in port:
                    subsystem.add_connection((port, in_port[index_in].get_port_info()[0]))
                    index_in += 1
                if 'RConn' in port:
                    subsystem.add_connection((port, out_port[index_out].get_port_info()[0]))
                    index_out += 1
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_sensor_subsystem(self, max_num_component=3, seed=None):
        if seed:
            random.seed(seed)
        subsystem = Subsystem(subsystem_type='sensor')
        num_sensors = random.randint(1, max_num_component)
        for i in range(num_sensors):
            component = self.component_factory.create_sensor(seed=seed)
            converter = self.component_factory.create_utilities('PSSimuConv')
            scope = self.component_factory.create_utilities('Scope')
            to_workspace = self.component_factory.create_workspace('ToWorkspace')
            subsystem.add_component(component, converter, scope, to_workspace)
        #connect with scope ports
        sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
        voltage_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'VoltageSensor']
        current_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'CurrentSensor']
        converters = [converter for converter in subsystem.component_list if converter.name == 'PSSimuConv']
        to_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
        scopes = [scope for scope in subsystem.component_list if scope.name == 'Scope']
        index_scope = 0
        for sensor in sensors:
            for port in sensor.get_port_info():
                if 'scope' in port:
                    subsystem.add_connection((port.replace('scope', ''), converters[index_scope].get_port_info()[0]),
                                             (converters[index_scope].get_port_info()[1], scopes[index_scope].get_port_info()[0]),
                                             (converters[index_scope].get_port_info()[1], to_workspace[index_scope].get_port_info()[0]))
                    index_scope += 1
        #add in and out port
        inport = self.component_factory.create_port('Inport', type='electrical')
        outport = self.component_factory.create_port('Outport', type='electrical')
        subsystem.add_component(inport, outport)
        in_port = [port_class for port_class in subsystem.component_list if
                   port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if
                    port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        if voltage_sensors and current_sensors:
            subsystem.subsystem_type = 'sensor_both'
            inport1 = self.component_factory.create_port('Inport', type='electrical')
            subsystem.add_component(inport1)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem = self.series_connect(subsystem, current_sensors, [in_port[0]], [in_port[1]])
            subsystem = self.parallel_connect(subsystem, voltage_sensors, [in_port[1]], out_port)
        elif voltage_sensors:
            subsystem.subsystem_type = 'sensor_voltage'
            subsystem = self.parallel_connect(subsystem, voltage_sensors, in_port, out_port)
        elif current_sensors:
            subsystem.subsystem_type = 'sensor_current'
            subsystem = self.series_connect(subsystem, current_sensors, in_port, out_port)
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_mission_subsystem(self, name=None, seed=None):
        if seed:
            random.seed(seed)
        if not name:
            name = random.choice(['IncandescentLamp'])
        subsystem = Subsystem(subsystem_type='mission')
        mission = self.component_factory.create_mission_object(name)
        subsystem.add_component(mission)
        if name == 'UniversalMotor':
            mechanical = self.component_factory.create_mission_object('Inertia')
            subsystem.add_component(mechanical)
            subsystem.add_connection((mission.get_port_info()[-1], mechanical.get_port_info()[-1]),
                                     (mission.get_port_info()[-2], mechanical.get_port_info()[-2]))
        if name == 'IncandescentLamp' or name == 'UniversalMotor':
            for sensor_name in ['VoltageSensor', 'CurrentSensor']:
                sensor = self.component_factory.create_sensor(sensor_name)
                converter = self.component_factory.create_utilities('PSSimuConv')
                scope = self.component_factory.create_utilities('Scope')
                to_workspace = self.component_factory.create_workspace('ToWorkspace')
                subsystem.add_component(sensor, converter, scope, to_workspace)
            #add sensor
            sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
            mission = [comp for comp in subsystem.component_list if comp.name == name]
            voltage_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'VoltageSensor']
            current_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'CurrentSensor']
            converters = [converter for converter in subsystem.component_list if converter.name == 'PSSimuConv']
            to_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
            scopes = [scope for scope in subsystem.component_list if scope.name == 'Scope']
            index_scope = 0
            for sensor in sensors:
                for port in sensor.get_port_info():
                    if 'scope' in port:
                        subsystem.add_connection(
                            (port.replace('scope', ''), converters[index_scope].get_port_info()[0]),
                            (converters[index_scope].get_port_info()[1], scopes[index_scope].get_port_info()[0]),
                            (converters[index_scope].get_port_info()[1], to_workspace[index_scope].get_port_info()[0]))
                        index_scope += 1
            #add ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            #connect
            for port in current_sensors[0].get_port_info():
                if '+' in port:
                    subsystem.add_connection((port.replace('+', ''), in_port[0].get_port_info()[0]))
                if '-' in port:
                    for comp in [mission[0], voltage_sensors[0]]:
                        for port_1 in comp.get_port_info():
                            if '+' in port_1:
                                subsystem.add_connection((port_1.replace('+', ''), port.replace('-', '')))
                            if '-' in port_1:
                                subsystem.add_connection((port_1.replace('-', ''), out_port[0].get_port_info()[0]))
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem


    def build_base_circuit(self, element_sys, soursys):
        subset_size = random.randint(1, len(element_sys))
        parallel_elements = random.sample(element_sys, subset_size)
        for elesys in parallel_elements:
            for inport in elesys.inport_info:
                self._model.add_connection((inport, soursys.inport_info[0]))
            for outport in elesys.outport_info:
                self._model.add_connection((outport, soursys.outport_info[0]))
            self._model.add_connection()
            element_sys.remove(elesys)
        return element_sys

    def add_series_connections(self, subsys, base_port, port_1, port_2):
        if 'inport' in base_port:
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        else:
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_2))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_1))

    def add_series_subsys(self, subsys, type, exclude_paths=None, connections=None):
        if type == 'element':
            connection = random.choice(self._model.connections)
            self._model.connections.remove(connection)
            base_port = connection[0]
            port_1 = connection[1]
            port_2 = connection[0]
            self.add_series_connections(subsys, base_port, port_1, port_2)
        if type == 'source':
            length = []
            connection = random.choice(self._model.connections)
            if any(connection in sublist for path in exclude_paths for sublist in path):
                for path in exclude_paths:
                    if any(connection in sublist for sublist in path):
                        length.append(len(path))
                if all(value > 1 for value in length):
                    exclude_paths = [[sublist for sublist in path if connection not in sublist] for path in
                                     exclude_paths]
            while any(connection in sublist for path in exclude_paths for sublist in path) and any(
                    value == 1 for value in length):
                connection = random.choice(self._model.connections)
            self._model.connections.remove(connection)
            base_port = connection[0]
            port_1 = connection[0]
            port_2 = connection[1]
            self.add_series_connections(subsys, base_port, port_1, port_2)
        if type == 'sensor':
            connection = random.choice(connections)
            while connection not in self._model.connections:
                connection = random.choice(connections)
            self._model.connections.remove(connection)
            # connections.remove(connection)
            if 'source' in connection:
                s_port = [x for x in connection if 'source' in x]
                remain_port = [x for x in connection if x != s_port[0]]
                base_port = s_port[0]
                port_1 = s_port[0]
                port_2 = remain_port[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)
            else:
                base_port = connection[0]
                port_1 = connection[1]
                port_2 = connection[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)

    def add_parallel_subsys(self, subsys, type, exclude_ports=None, source_sys=None, connections_sensor=None):
        connections = self._model.connections.copy()
        if type == 'element':
            connection_1 = random.choice(connections)
            port_1 = random.choice(connection_1)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            exclude_ports = self._model.extract_elements(
                [port_1])
            port_2 = port_1
            while port_2 in exclude_ports[0]:
                connection = random.choice(connections)
                port_2 = random.choice(connection)
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        if type == 'source':
            port_1 = source_sys[0].inport_info[0]
            port_2 = source_sys[0].outport_info[0]
            while any(port_1 in sublist for sublist in exclude_ports) and any(port_2 in sublist
                                                                              for sublist in exclude_ports):
                connection_1 = random.choice(connections)
                port_1 = random.choice(connection_1)
                exclude_connection = self._model.extract_elements([port_1])
                connection = random.choice(connections)
                port_2 = random.choice(connection)
                while port_2 in exclude_connection[0]:
                    connection = random.choice(connections)
                    port_2 = random.choice(connection)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        if type == 'sensor':
            port_1 = 'p'
            while 'inport' not in port_1:
                connection_1 = random.choice(connections_sensor)
                port_1 = random.choice(connection_1)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            exclude_ports = self._model.extract_elements([port_1], connections=connections_sensor)
            port_2 = port_1
            while port_2 in exclude_ports[0]:
                connection = random.choice(connections_sensor)
                port_2 = random.choice(connection)
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))

    def add_element_subsys(self, element_sys):
        while element_sys:
            subset_size = random.randint(1, len(element_sys))
            subset = random.sample(element_sys, subset_size)
            element_sys = [x for x in element_sys if x not in subset]
            series_elements_size = random.randint(1, len(subset))
            series_elements = random.sample(subset, series_elements_size)
            subset = [x for x in subset if x not in series_elements]
            for elesys in series_elements:
                self.add_series_subsys(elesys, 'element')
            if subset:
                for elesys in subset:
                    self.add_parallel_subsys(elesys, 'element')

    def add_mission_subsys(self, mission_sys):
        if len(mission_sys) == 1:
            type = random.choice(['s', 'p'])
            if type == 's':
                self.add_series_subsys(mission_sys[0], 'element')
            if type == 'p':
                self.add_parallel_subsys(mission_sys[0], 'element')
        else:
            while mission_sys:
                subset_size = random.randint(1, len(mission_sys))
                subset = random.sample(mission_sys, subset_size)
                mission_sys = [x for x in mission_sys if x not in subset]
                series_mission_size = random.randint(1, len(subset))
                series_mission = random.sample(subset, series_mission_size)
                subset = [x for x in subset if x not in series_mission]
                for missionsys in series_mission:
                    self.add_series_subsys(missionsys, 'element')
                if subset:
                    for missionsys in subset:
                        self.add_parallel_subsys(missionsys, 'element')

    def check_circuit_source(self, exclude_paths, exclude_ports):
        type_p = 0
        type_s = 0
        involved_num = []
        for connection in self._model.connections:
            for i, path in enumerate(exclude_paths):
                involved_path = 0
                for sublist in path:
                    if connection in sublist:
                        involved_path += 1
                if involved_path > 0:
                    involved_num.append(involved_path)
            length_path = [len(path) for path in exclude_paths if any(connection in sublist for sublist in path)]
            empty_path = [a - b for a, b in zip(length_path, involved_num)]
            if all(connection not in sublist for path in exclude_paths for sublist in path) or all(
                    value > 1 for value in empty_path):
                type_s += 1
            for port in connection:
                if all(port not in sublist for sublist in exclude_ports):
                    type_p += 1
        if type_s and type_p:
            type = random.choice(['s', 'p'])
        elif type_s:
            type = 's'
        elif type_p:
            type = 'p'
        else:
            type = 'full'
        return type

    def add_source_subsys(self, source_sys):
        exclude_ports = self._model.extract_elements([source_sys[0].inport_info[0], source_sys[0].outport_info[0]])
        path = self._model.find_paths(source_sys[0].inport_info[0], source_sys[0].outport_info[0])
        exclude_paths = [path]
        for soursys in source_sys[1:]:
            type = self.check_circuit_source(exclude_paths, exclude_ports)
            if type == 'full':
                self._model.subsystem_list.remove(soursys)
                continue
            if type == 'p':
                self.add_parallel_subsys(soursys, 'source', exclude_ports=exclude_ports, source_sys=source_sys)
            if type == 's':
                self.add_series_subsys(soursys, 'source', exclude_paths=exclude_paths)
            exports = self._model.extract_elements([soursys.inport_info[0], soursys.outport_info[0]])
            exclude_ports.extend(exports)
            expath = self._model.find_paths(soursys.inport_info[0], soursys.outport_info[0])
            exclude_paths.append(expath)

    def add_main_sensor(self, subsys, connections):
        connection = random.choice(connections)
        while connection not in self._model.connections:
            connection = random.choice(connections)
        port = random.choice(connection)
        all_related_connections = self._model.filter_connections([port])
        i = 0
        for connection in all_related_connections[0]:
            self._model.connections.remove(connection)
            # connections.remove(connection)
            remain_port = [x for x in connection if x != port]
            if 'source' in port:
                if 'inport' in port:
                    if i == 0:
                        for inport in subsys.inport_info:
                            self._model.add_connection((inport, port))
                        i += 1
                    for outport in subsys.outport_info:
                        self._model.add_connection((outport, remain_port[0]))
                if 'outport' in port:
                    for inport in subsys.inport_info:
                        self._model.add_connection((inport, remain_port[0]))
                    if i == 0:
                        for outport in subsys.outport_info:
                            self._model.add_connection((outport, port))
                        i += 1
            else:
                if 'inport' in port:
                    for inport in subsys.inport_info:
                        self._model.add_connection((inport, remain_port[0]))
                    if i == 0:
                        for outport in subsys.outport_info:
                            self._model.add_connection((outport, port))
                        i += 1
                else:
                    if i == 0:
                        for inport in subsys.inport_info:
                            self._model.add_connection((inport, port))
                        i += 1
                    for outport in subsys.outport_info:
                        self._model.add_connection((outport, remain_port[0]))

    def add_sensor_subsys(self, sensor_sys):
        connections = self._model.connections.copy()
        connections_sensor = self._model.connections.copy()
        for sensys in sensor_sys:
            # connections = self._model.connections.copy()
            if sensys.subsystem_type == 'sensor_voltage':
                self.add_parallel_subsys(sensys, 'sensor', connections_sensor=connections_sensor)
            if sensys.subsystem_type == 'sensor_current':
                type = random.choice(['branch', 'main'])
                if type == 'branch':
                    self.add_series_subsys(sensys, 'sensor', connections=connections)
                if type == 'main':
                    self.add_main_sensor(sensys, connections)
            if sensys.subsystem_type == 'sensor_both':
                connection = random.choice(connections)
                port = random.choice(connection)
                while 'inport' not in port or connection not in self._model.connections:
                    connection = random.choice(connections)
                    port = random.choice(connection)
                all_related_connections = self._model.filter_connections([port])
                self._model.add_connection((sensys.inport_info[1], port))
                for connection in all_related_connections[0]:
                    self._model.connections.remove(connection)
                    # connections.remove(connection)
                    remain_port = [x for x in connection if x != port]
                    self._model.add_connection((sensys.inport_info[0], remain_port[0]))
                # take the measured subsystem
                id_index = port.find('id')
                underscore_index = port.find('_', id_index)
                id = int(port[id_index + 2:underscore_index])
                subsystem = [subsystem for subsystem in self._model.subsystem_list if subsystem.name ==
                             port.split('_', 1)[0] and subsystem.ID == id]
                self._model.add_connection((sensys.outport_info[0], subsystem[0].outport_info[0]))

    def add_switch_subsys(self, num_actuators, seed):
        connections = self._model.connections.copy()
        for i in range(num_actuators):
            num_pole = random.randint(1, 1)
            connection = random.choice(connections)
            while any('sensor_voltage' in p for p in connection) or any(
                    'sensor_both' and 'outport' in p for p in connection):
                connection = random.choice(connections)
            port = random.choice(connection)
            related_connections = self._model.filter_connections([port])
            all_related_connections = [[p for p in related_connections[0] if ('sensor_voltage' not in p)
                                        and ('sensor_both' and 'outport' not in p)]]
            num_connections = random.randint(1, len(all_related_connections[0]))
            while num_connections > 8:
                num_connections = random.randint(1, len(all_related_connections[0]))
            all_related_connections = random.sample(all_related_connections[0], num_connections)
            switchsys = self.create_actuator_subsystem(seed=seed, pole_and_throw=[num_pole, num_connections])
            self._model.add_subsystem(switchsys)
            self._model.add_connection((switchsys.inport_info[0], port))
            i = 0
            for connection in all_related_connections:
                self._model.connections.remove(connection)
                connections.remove(connection)
                remain_port = [x for x in connection if x != port]
                self._model.add_connection((switchsys.outport_info[i], remain_port[0]))
                i += 1

    def build_subsystem(self, max_num_source=3, max_num_sensor=2, max_num_acuator=2, max_num_element=5,
                        max_num_mission=1, mission_name=None, seed=None):
    # def build_subsystem(self, max_num_source=5, max_num_sensor=3, max_num_acuator=2, max_num_element=10, max_num_mission=1, mission_name=None, seed=None):
        if seed:
            random.seed(seed)
        num_sensors = random.randint(1, max_num_sensor)
        num_elements = random.randint(1, max_num_element)
        num_sources = random.randint(1, max_num_source)
        num_actuators = random.randint(1, max_num_acuator)
        num_mission = random.randint(1, max_num_mission)
        for i in range(num_sources):
            type = random.choice(['voltage', 'current'])
            subsys = self.create_source_subsystem(type=type, seed=seed)
            self._model.add_subsystem(subsys)
        for i in range(num_elements):
            subsys = self.create_element_subsystem(seed=seed)
            self._model.add_subsystem(subsys)
        num_current_sensor = 0
        for i in range(num_sensors):
            subsys = self.create_sensor_subsystem(seed=seed)
            if subsys.subsystem_type in ['sensor_current', 'sensor_both'] and num_current_sensor < num_elements:
                num_current_sensor += 1
                self._model.add_subsystem(subsys)
            else:
                while subsys.subsystem_type in ['sensor_current', 'sensor_both']:
                    subsys = self.create_sensor_subsystem(seed=seed)
                self._model.add_subsystem(subsys)
        for i in range(num_mission):
            mission_subsys = self.create_mission_subsystem(name=mission_name, seed=seed)
            self._model.add_subsystem(mission_subsys)
        sensor_sys = [subsys for subsys in self._model.subsystem_list if 'sensor' in subsys.subsystem_type]
        element_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'element']
        mission_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'mission']
        source_sys = [subsys for subsys in self._model.subsystem_list if 'source' in subsys.subsystem_type]
        # #biuld base circuit
        element_sys = self.build_base_circuit(element_sys, source_sys[0])
        # add elements
        self.add_element_subsys(element_sys)
        #add mission
        self.add_mission_subsys(mission_sys)
        #add source
        self.add_source_subsys(source_sys)
        #add sensor
        self.add_sensor_subsys(sensor_sys)
        #add switch
        self.add_switch_subsys(num_actuators, seed)



    def random_single_connect(self, component):
        connection = random.choice(self._model.connections)
        port = random.choice(connection)
        self._model.add_connection((port, component.get_port_info()[0]))

    def set_workspace(self):
        i = 0
        for component in self._model.component_list:
            if component.name == 'ToWorkspace':
                component.variable_name = f"simout_{i}"
                i = i + 1
        for subsys in self._model.subsystem_list:
            i = 0
            for component in subsys.component_list:
                if component.name == 'ToWorkspace':
                    component.variable_name = f"{subsys.subsystem_type}_{subsys.ID}_simout_{i}"
                    i = i + 1

    def build_component(self, seed=None):
        if seed:
            random.seed(seed)
        solver = self.component_factory.create_utilities('Solver')
        reference = self.component_factory.create_utilities('Reference')
        self._model.add_component(solver, reference)
        self.random_single_connect(reference)
        self.random_single_connect(solver)


    def build_system(self, max_num_source=3, max_num_sensor=2, max_num_acuator=2, max_num_element=5, max_num_mission=1,
                     mission_name=None, seed=None):
        if seed:
            random.seed(seed)
        self.build_subsystem(max_num_source=max_num_source, max_num_sensor=max_num_sensor, max_num_acuator=max_num_acuator,
                             max_num_element=max_num_element, max_num_mission=max_num_mission, mission_name=mission_name)
        self.build_component()
        self.set_workspace()


@gin.configurable
class DCBuilder(ElectricalModelBuilder):
    def __init__(self, max_source_component=4, max_element_component=5, max_sensor_component=3):
        super().__init__(DCComponentFactory())
        self.reset()
        self.max_source_component = max_source_component
        self.max_element_component = max_element_component
        self.max_sensor_component = max_sensor_component

    def reset(self):
        self._model = System()

    def product(self):
        model = self._model
        return model

    def series_connect(self, subsys, component, inport, outport):
        subsystem = subsys
        comp = component
        in_port = inport
        out_port = outport
        comp_port = [obj.get_port_info() for obj in comp]
        if len(comp_port) == 1:
            list_first = [elem for elem in comp_port[0] if '+' in elem]
            subsystem.add_connection((list_first[0].replace('+', ''), in_port[0].get_port_info()[0]))
            list_last = [elem for elem in comp_port[0] if '-' in elem]
            subsystem.add_connection((list_last[0].replace('-', ''), out_port[0].get_port_info()[0]))
        else:
            for i in range(len(comp_port) - 1):
                list_negative = [elem for elem in comp_port[i] if '-' in elem]
                list_positive = [elem for elem in comp_port[i + 1] if '+' in elem]
                if i == 0:
                    list_first = [elem for elem in comp_port[i] if '+' in elem]
                    subsystem.add_connection((list_first[0].replace('+', ''), in_port[0].get_port_info()[0]))
                if i == len(comp_port) - 2:
                    list_last = [elem for elem in comp_port[i+1] if '-' in elem]
                    subsystem.add_connection((list_last[0].replace('-', ''), out_port[0].get_port_info()[0]))
                new_connect = (list_positive[0].replace('+', ''), list_negative[0].replace('-', ''))
                subsystem.add_connection(new_connect)
        return subsystem

    def parallel_connect(self, subsys, component, inport, outport):
        subsystem = subsys
        comp = component
        in_port = inport
        out_port = outport
        for comp in comp:
            for port in comp.get_port_info():
                if '+' in port:
                    subsystem.add_connection((port.replace('+', ''), in_port[0].get_port_info()[0]))
                if '-' in port:
                    subsystem.add_connection((port.replace('-', ''), out_port[0].get_port_info()[0]))
        return subsystem


    def create_source_subsystem(self, type, seed=None, battery_exsist=None):
        if seed:
            random.seed(seed)
        max_num_component = self.max_source_component
        if type == 'voltage':
            subsystem = Subsystem(subsystem_type='source_voltage')
            num_sources = random.randint(1, max_num_component)
            for i in range(num_sources):
                if battery_exsist:
                    type = random.choice(['voltage', 'battery'])
                    component = self.component_factory.create_source(type=type, seed=seed)
                else:
                    component = self.component_factory.create_source(type='voltage', seed=seed)
                subsystem.add_component(component)
            #connent to signal
            comp = [comp for comp in subsystem.component_list if comp.component_type == 'Source']
            comp_port = [obj.get_port_info() for obj in comp]
            list_signal = []
            for i in range(len(comp_port)):
                list = [elem for elem in comp_port[i] if 'signal' in elem]
                list_signal.extend(list)
            if list_signal:
                for i in range(len(list_signal)):
                    from_workspace = self.component_factory.create_workspace('FromWorkspace')
                    converter = self.component_factory.create_utilities('SimuPSConv')
                    subsystem.add_component(from_workspace, converter)
                from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
                converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
                index_sig = 0
                for port in list_signal:
                        subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1]),
                                                 (converter[index_sig].get_port_info()[0], from_workspace[index_sig].get_port_info()[0]))
                        index_sig += 1
            # connect with ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem_connected = self.series_connect(subsystem, comp, in_port, out_port)
        if type == 'current':
            subsystem = Subsystem(subsystem_type='source_current')
            num_sources = random.randint(1, max_num_component)
            for i in range(num_sources):
                component = self.component_factory.create_source(type='current', seed=seed)
                subsystem.add_component(component)
            #connent to signal
            comp = [comp for comp in subsystem.component_list if comp.component_type == 'Source']
            comp_port = [obj.get_port_info() for obj in comp]
            list_signal = []
            for i in range(len(comp_port)):
                list = [elem for elem in comp_port[i] if 'signal' in elem]
                list_signal.extend(list)
            if list_signal:
                for i in range(len(list_signal)):
                    from_workspace = self.component_factory.create_workspace('FromWorkspace')
                    converter = self.component_factory.create_utilities('SimuPSConv')
                    subsystem.add_component(from_workspace, converter)
                from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
                converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
                index_sig = 0
                for port in list_signal:
                        subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                                 , (converter[index_sig].get_port_info()[0],
                                                    from_workspace[index_sig].get_port_info()[0]))
                        index_sig += 1
            # connect with ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem_connected = self.parallel_connect(subsystem, comp, in_port, out_port)
        if type == 'battery':
            subsystem = Subsystem(subsystem_type='source_battery')
            num_sources = random.randint(1, max_num_component)
            seed_b = random.randint(1, 100)
            for i in range(num_sources):
                component = self.component_factory.create_source(name='Battery', seed=seed_b)
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            comp = [comp for comp in subsystem.component_list if comp.component_type == 'Source']
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            type_b = random.choice(['s','p'])
            if type_b == 's':
                subsystem_connected = self.series_connect(subsystem, comp, in_port, out_port)
            if type_b == 'p':
                subsystem_connected = self.parallel_connect(subsystem, comp, in_port, out_port)
        subsystem_connected.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem_connected.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem_connected

    def create_element_subsystem(self, seed=None):
        subsystem = Subsystem(subsystem_type='element')
        if seed:
            random.seed(seed)
        max_num_component = self.max_element_component
        #create elements randomly
        num_components = random.randint(1, max_num_component)
        for i in range(num_components):
            component = self.component_factory.create_element(seed=seed)
            subsystem.add_component(component)
        group = [element for element in subsystem.component_list if element.component_type == 'Element']
        chosen_pair = []
        first_component = random.choice(group)
        all_ports = first_component.get_port_info()
        group.remove(first_component)
        connected_components = [first_component]
        while group:
            component = random.choice(group)
            new_ports = component.get_port_info()
            all_ports.extend(new_ports)
            port_pairs = []
            for c in connected_components:
                # generate all possible port pairs between the new component and the connected components
                connected_ports = c.get_port_info()
                for np in new_ports:
                    for cp in connected_ports:
                        port_pairs.append((np, cp))
            # choose a random port pair and connect the components
            port_pair = random.choice(port_pairs)
            chosen_pair.append(port_pair)
            subsystem.add_connection(port_pair)
            connected_components.append(component)
            group.remove(component)
        #find out unused ports
        unused_port = [port for port in all_ports if
                          port not in [pair[0] for pair in chosen_pair] and port not in
                          [pair[1] for pair in chosen_pair]]
        #add input and output for subsystem
        inport = self.component_factory.create_port('Inport', type='electrical')
        outport = self.component_factory.create_port('Outport', type='electrical')
        subsystem.add_component(inport,outport)
        n = random.randint(0, len(unused_port)-2)
        for i in range(n):
            port_name = random.choice(['Inport', 'Outport'])
            port = self.component_factory.create_port(port_name, type='electrical')
            subsystem.add_component(port)
        #connect components with input and output
        subsystem_port = [port_class for port_class in subsystem.component_list if port_class.component_type == 'Port']
        in_out_ports = []
        for port in subsystem_port:
            in_out_ports.extend(port.get_port_info())
        in_out_ports_copy = in_out_ports.copy()
        for item2 in unused_port:
            if len(in_out_ports_copy) == 0:
                in_out_ports_copy = in_out_ports.copy()
            item1 = random.choice(in_out_ports_copy)
            subsystem.add_connection((item1, item2))
            in_out_ports_copy.remove(item1)
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_actuator_subsystem(self, seed=None, pole_and_throw=None):
        subsystem = Subsystem(subsystem_type='switch')
        if seed:
            random.seed(seed)
        component = self.component_factory.create_actuator(seed=seed, pole_and_throw=pole_and_throw)
        subsystem.add_component(component)
        switchs = [switch for switch in subsystem.component_list if switch.component_type == 'Actuator']
        for switch in switchs:
            for i in range(len(switch.take_port('LConn')) - 1):
                inport = self.component_factory.create_port('Inport', type='electrical')
                subsystem.add_component(inport)
            for i in range(len(switch.take_port('RConn'))):
                outport = self.component_factory.create_port('Outport', type='electrical')
                subsystem.add_component(outport)
            from_workspace = self.component_factory.create_workspace('FromWorkspace')
            converter = self.component_factory.create_utilities('SimuPSConv')
            subsystem.add_component(from_workspace, converter)
        #connect with port
        in_port = [port_class for port_class in subsystem.component_list if
                   port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if
                    port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        from_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
        converter = [converter for converter in subsystem.component_list if converter.name == 'SimuPSConv']
        index_sig = 0
        index_in = 0
        index_out = 0
        for switch in switchs:
            for port in switch.get_port_info():
                if 'signal' in port:
                    subsystem.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                             ,(converter[index_sig].get_port_info()[0],from_workspace[index_sig].get_port_info()[0]))
                    index_sig += 1
                if 'LConn' in port and 'signal' not in port:
                    subsystem.add_connection((port, in_port[index_in].get_port_info()[0]))
                    index_in += 1
                if 'RConn' in port:
                    subsystem.add_connection((port, out_port[index_out].get_port_info()[0]))
                    index_out += 1
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_sensor_subsystem(self, seed=None):
        if seed:
            random.seed(seed)
        subsystem = Subsystem(subsystem_type='sensor')
        max_num_component = self.max_sensor_component
        num_sensors = random.randint(1, max_num_component)
        for i in range(num_sensors):
            component = self.component_factory.create_sensor(seed=seed)
            converter = self.component_factory.create_utilities('PSSimuConv')
            scope = self.component_factory.create_utilities('Scope')
            to_workspace = self.component_factory.create_workspace('ToWorkspace')
            subsystem.add_component(component, converter, scope, to_workspace)
        #connect with scope ports
        sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
        voltage_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'VoltageSensor']
        current_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'CurrentSensor']
        converters = [converter for converter in subsystem.component_list if converter.name == 'PSSimuConv']
        to_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
        scopes = [scope for scope in subsystem.component_list if scope.name == 'Scope']
        index_scope = 0
        for sensor in sensors:
            for port in sensor.get_port_info():
                if 'scope' in port:
                    subsystem.add_connection((port.replace('scope', ''), converters[index_scope].get_port_info()[0]),
                                             (converters[index_scope].get_port_info()[1], scopes[index_scope].get_port_info()[0]),
                                             (converters[index_scope].get_port_info()[1], to_workspace[index_scope].get_port_info()[0]))
                    index_scope += 1
        #add in and out port
        inport = self.component_factory.create_port('Inport', type='electrical')
        outport = self.component_factory.create_port('Outport', type='electrical')
        subsystem.add_component(inport, outport)
        in_port = [port_class for port_class in subsystem.component_list if
                   port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if
                    port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        if voltage_sensors and current_sensors:
            subsystem.subsystem_type = 'sensor_both'
            inport1 = self.component_factory.create_port('Inport', type='electrical')
            subsystem.add_component(inport1)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            subsystem = self.series_connect(subsystem, current_sensors, [in_port[0]], [in_port[1]])
            subsystem = self.parallel_connect(subsystem, voltage_sensors, [in_port[1]], out_port)
        elif voltage_sensors:
            subsystem.subsystem_type = 'sensor_voltage'
            subsystem = self.parallel_connect(subsystem, voltage_sensors, in_port, out_port)
        elif current_sensors:
            subsystem.subsystem_type = 'sensor_current'
            subsystem = self.series_connect(subsystem, current_sensors, in_port, out_port)
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem

    def create_mission_subsystem(self, name=None, seed=None):
        if seed:
            random.seed(seed)
        if not name:
            name = random.choice(['IncandescentLamp'])
        subsystem = Subsystem(subsystem_type='mission')
        mission = self.component_factory.create_mission_object(name)
        subsystem.add_component(mission)
        if name == 'UniversalMotor':
            mechanical = self.component_factory.create_mission_object('Inertia')
            subsystem.add_component(mechanical)
            subsystem.add_connection((mission.get_port_info()[-1], mechanical.get_port_info()[-1]),
                                     (mission.get_port_info()[-2], mechanical.get_port_info()[-2]))
        if name == 'IncandescentLamp' or name == 'UniversalMotor':
            for sensor_name in ['VoltageSensor', 'CurrentSensor']:
                sensor = self.component_factory.create_sensor(sensor_name)
                converter = self.component_factory.create_utilities('PSSimuConv')
                scope = self.component_factory.create_utilities('Scope')
                to_workspace = self.component_factory.create_workspace('ToWorkspace')
                subsystem.add_component(sensor, converter, scope, to_workspace)
            #add sensor
            sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
            mission = [comp for comp in subsystem.component_list if comp.name == name]
            voltage_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'VoltageSensor']
            current_sensors = [sensor for sensor in subsystem.component_list if sensor.name == 'CurrentSensor']
            converters = [converter for converter in subsystem.component_list if converter.name == 'PSSimuConv']
            to_workspace = [wp for wp in subsystem.component_list if wp.component_type == 'Workspace']
            scopes = [scope for scope in subsystem.component_list if scope.name == 'Scope']
            index_scope = 0
            for sensor in sensors:
                for port in sensor.get_port_info():
                    if 'scope' in port:
                        subsystem.add_connection(
                            (port.replace('scope', ''), converters[index_scope].get_port_info()[0]),
                            (converters[index_scope].get_port_info()[1], scopes[index_scope].get_port_info()[0]),
                            (converters[index_scope].get_port_info()[1], to_workspace[index_scope].get_port_info()[0]))
                        index_scope += 1
            #add ports
            inport = self.component_factory.create_port('Inport', type='electrical')
            outport = self.component_factory.create_port('Outport', type='electrical')
            subsystem.add_component(inport, outport)
            in_port = [port_class for port_class in subsystem.component_list if
                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if
                        port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
            #connect
            for port in current_sensors[0].get_port_info():
                if '+' in port:
                    subsystem.add_connection((port.replace('+', ''), in_port[0].get_port_info()[0]))
                if '-' in port:
                    for comp in [mission[0], voltage_sensors[0]]:
                        for port_1 in comp.get_port_info():
                            if '+' in port_1:
                                subsystem.add_connection((port_1.replace('+', ''), port.replace('-', '')))
                            if '-' in port_1:
                                subsystem.add_connection((port_1.replace('-', ''), out_port[0].get_port_info()[0]))
        subsystem.inport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [f'{port_class.name}_{port_class.ID}' for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem


    def build_base_circuit(self, element_sys, soursys):
        subset_size = random.randint(1, len(element_sys))
        parallel_elements = random.sample(element_sys, subset_size)
        for elesys in parallel_elements:
            for inport in elesys.inport_info:
                self._model.add_connection((inport, soursys.inport_info[0]))
            for outport in elesys.outport_info:
                self._model.add_connection((outport, soursys.outport_info[0]))
            self._model.add_connection()
            element_sys.remove(elesys)
        return element_sys

    def add_series_connections(self, subsys, base_port, port_1, port_2):
        if 'inport' in base_port:
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        else:
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_2))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_1))

    def add_series_subsys(self, subsys, type, exclude_paths=None, connections=None):
        if type == 'element':
            connection = random.choice(self._model.connections)
            self._model.connections.remove(connection)
            if 'source' in connection:
                s_port = [x for x in connection if 'source' in x]
                remain_port = [x for x in connection if x != s_port[0]]
                base_port = s_port[0]
                port_1 = s_port[0]
                port_2 = remain_port[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)
            else:
                base_port = connection[0]
                port_1 = connection[1]
                port_2 = connection[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)
        if type == 'source':
            length = []
            connection = random.choice(self._model.connections)
            if any(connection in sublist for path in exclude_paths for sublist in path):
                for path in exclude_paths:
                    if any(connection in sublist for sublist in path):
                        length.append(len(path))
                if all(value > 1 for value in length):
                    exclude_paths = [[sublist for sublist in path if connection not in sublist] for path in
                                     exclude_paths]
            while any(connection in sublist for path in exclude_paths for sublist in path) and any(
                    value == 1 for value in length):
                connection = random.choice(self._model.connections)
            self._model.connections.remove(connection)
            if any('source' in p for p in connection):
                s_port = [x for x in connection if 'source' in x]
                remain_port = [x for x in connection if x != s_port[0]]
                base_port = s_port[0]
                port_1 = remain_port[0]
                port_2 = s_port[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)
            else:
                base_port = connection[0]
                port_1 = connection[0]
                port_2 = connection[1]
                self.add_series_connections(subsys, base_port, port_1, port_2)
        if type == 'sensor':
            connection = random.choice(connections)
            while connection not in self._model.connections:
                connection = random.choice(connections)
            self._model.connections.remove(connection)
            # connections.remove(connection)
            if 'source' in connection:
                s_port = [x for x in connection if 'source' in x]
                remain_port = [x for x in connection if x != s_port[0]]
                base_port = s_port[0]
                port_1 = s_port[0]
                port_2 = remain_port[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)
            else:
                base_port = connection[0]
                port_1 = connection[1]
                port_2 = connection[0]
                self.add_series_connections(subsys, base_port, port_1, port_2)

    def add_parallel_subsys(self, subsys, type, exclude_ports=None, source_sys=None, connections_sensor=None):
        connections = self._model.connections.copy()
        if type == 'element':
            port_1 = 'p'
            while 'inport' not in port_1 or 'source' in port_1:
                connection_1 = random.choice(connections)
                port_1 = random.choice(connection_1)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            exclude_ports = self._model.extract_elements(
                [port_1])
            port_2 = 'p'
            while 'outport' not in port_2 or 'source' in port_2 or port_2 in exclude_ports[0]:
                connection = random.choice(connections)
                port_2 = random.choice(connection)
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        if type == 'source':
            port_1 = source_sys[0].inport_info[0]
            port_2 = source_sys[0].outport_info[0]
            while any(port_1 in sublist for sublist in exclude_ports) and any(port_2 in sublist
                                                                              for sublist in exclude_ports):
                connection_1 = random.choice(connections)
                port_1 = random.choice(connection_1)
                while 'inport' not in port_1:
                    connection_1 = random.choice(connections)
                    port_1 = random.choice(connection_1)
                exclude_connection = self._model.extract_elements([port_1])
                connection = random.choice(connections)
                port_2 = random.choice(connection)
                while 'outport' not in port_2 or port_2 in exclude_connection[0]:
                    connection = random.choice(connections)
                    port_2 = random.choice(connection)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))
        if type == 'sensor':
            port_1 = 'p'
            while 'inport' not in port_1:
                connection_1 = random.choice(connections_sensor)
                port_1 = random.choice(connection_1)
            for inport in subsys.inport_info:
                self._model.add_connection((inport, port_1))
            exclude_ports = self._model.extract_elements([port_1], connections=connections_sensor)
            port_2 = 'p'
            while 'outport' not in port_2 or port_2 in exclude_ports[0]:
                connection = random.choice(connections_sensor)
                port_2 = random.choice(connection)
            for outport in subsys.outport_info:
                self._model.add_connection((outport, port_2))

    def add_element_subsys(self, element_sys):
        while element_sys:
            subset_size = random.randint(1, len(element_sys))
            subset = random.sample(element_sys, subset_size)
            element_sys = [x for x in element_sys if x not in subset]
            series_elements_size = random.randint(1, len(subset))
            series_elements = random.sample(subset, series_elements_size)
            subset = [x for x in subset if x not in series_elements]
            for elesys in series_elements:
                self.add_series_subsys(elesys, 'element')
            if subset:
                for elesys in subset:
                    self.add_parallel_subsys(elesys, 'element')

    def add_mission_subsys(self, mission_sys):
        if len(mission_sys) == 1:
            type = random.choice(['s', 'p'])
            if type == 's':
                self.add_series_subsys(mission_sys[0], 'element')
            if type == 'p':
                self.add_parallel_subsys(mission_sys[0], 'element')
        else:
            while mission_sys:
                subset_size = random.randint(1, len(mission_sys))
                subset = random.sample(mission_sys, subset_size)
                mission_sys = [x for x in mission_sys if x not in subset]
                series_mission_size = random.randint(1, len(subset))
                series_mission = random.sample(subset, series_mission_size)
                subset = [x for x in subset if x not in series_mission]
                for missionsys in series_mission:
                    self.add_series_subsys(missionsys, 'element')
                if subset:
                    for missionsys in subset:
                        self.add_parallel_subsys(missionsys, 'element')

    def check_circuit_source(self, exclude_paths, exclude_ports):
        type_p_in = 0
        type_p_out = 0
        type_s = 0
        involved_num = []
        for connection in self._model.connections:
            for i, path in enumerate(exclude_paths):
                involved_path = 0
                for sublist in path:
                    if connection in sublist:
                        involved_path += 1
                if involved_path > 0:
                    involved_num.append(involved_path)
            length_path = [len(path) for path in exclude_paths if any(connection in sublist for sublist in path)]
            empty_path = [a - b for a, b in zip(length_path, involved_num)]
            if all(connection not in sublist for path in exclude_paths for sublist in path) or all(
                    value > 1 for value in empty_path):
                type_s += 1
            for port in connection:
                if all(port not in sublist for sublist in exclude_ports):
                    if 'inport' in port:
                        type_p_in += 1
                    if 'outport' in port:
                        type_p_out += 1
        if type_s and type_p_in * type_p_out:
            type = random.choice(['s', 'p'])
        elif type_s:
            type = 's'
        elif type_p_in * type_p_out:
            type = 'p'
        else:
            type = 'full'
        return type

    def add_source_subsys(self, source_sys):
        exclude_ports = self._model.extract_elements([source_sys[0].inport_info[0], source_sys[0].outport_info[0]])
        path = self._model.find_paths(source_sys[0].inport_info[0], source_sys[0].outport_info[0])
        exclude_paths = [path]
        for soursys in source_sys[1:]:
            type = self.check_circuit_source(exclude_paths, exclude_ports)
            if type == 'full':
                self._model.subsystem_list.remove(soursys)
                continue
            if type == 'p':
                self.add_parallel_subsys(soursys, 'source', exclude_ports=exclude_ports, source_sys=source_sys)
            if type == 's':
                self.add_series_subsys(soursys, 'source', exclude_paths=exclude_paths)
            exports = self._model.extract_elements([soursys.inport_info[0], soursys.outport_info[0]])
            exclude_ports.extend(exports)
            expath = self._model.find_paths(soursys.inport_info[0], soursys.outport_info[0])
            exclude_paths.append(expath)

    def add_main_sensor(self, subsys, connections):
        connection = random.choice(connections)
        while connection not in self._model.connections:
            connection = random.choice(connections)
        port = random.choice(connection)
        all_related_connections = self._model.filter_connections([port])
        i = 0
        for connection in all_related_connections[0]:
            self._model.connections.remove(connection)
            # connections.remove(connection)
            remain_port = [x for x in connection if x != port]
            if 'source' in port:
                if 'inport' in port:
                    if i == 0:
                        for inport in subsys.inport_info:
                            self._model.add_connection((inport, port))
                        i += 1
                    for outport in subsys.outport_info:
                        self._model.add_connection((outport, remain_port[0]))
                if 'outport' in port:
                    for inport in subsys.inport_info:
                        self._model.add_connection((inport, remain_port[0]))
                    if i == 0:
                        for outport in subsys.outport_info:
                            self._model.add_connection((outport, port))
                        i += 1
            else:
                if 'inport' in port:
                    for inport in subsys.inport_info:
                        self._model.add_connection((inport, remain_port[0]))
                    if i == 0:
                        for outport in subsys.outport_info:
                            self._model.add_connection((outport, port))
                        i += 1
                else:
                    if i == 0:
                        for inport in subsys.inport_info:
                            self._model.add_connection((inport, port))
                        i += 1
                    for outport in subsys.outport_info:
                        self._model.add_connection((outport, remain_port[0]))

    def add_sensor_subsys(self, sensor_sys):
        connections = self._model.connections.copy()
        connections_sensor = self._model.connections.copy()
        for sensys in sensor_sys:
            # connections = self._model.connections.copy()
            if sensys.subsystem_type == 'sensor_voltage':
                self.add_parallel_subsys(sensys, 'sensor', connections_sensor=connections_sensor)
            if sensys.subsystem_type == 'sensor_current':
                type = random.choice(['branch', 'main'])
                if type == 'branch':
                    self.add_series_subsys(sensys, 'sensor', connections=connections)
                if type == 'main':
                    self.add_main_sensor(sensys, connections)
            if sensys.subsystem_type == 'sensor_both':
                connection = random.choice(connections)
                port = random.choice(connection)
                while 'inport' not in port or connection not in self._model.connections:
                    connection = random.choice(connections)
                    port = random.choice(connection)
                all_related_connections = self._model.filter_connections([port])
                self._model.add_connection((sensys.inport_info[1], port))
                for connection in all_related_connections[0]:
                    self._model.connections.remove(connection)
                    # connections.remove(connection)
                    remain_port = [x for x in connection if x != port]
                    self._model.add_connection((sensys.inport_info[0], remain_port[0]))
                # take the measured subsystem
                id_index = port.find('id')
                underscore_index = port.find('_', id_index)
                id = int(port[id_index + 2:underscore_index])
                subsystem = [subsystem for subsystem in self._model.subsystem_list if subsystem.name ==
                             port.split('_', 1)[0] and subsystem.ID == id]
                self._model.add_connection((sensys.outport_info[0], subsystem[0].outport_info[0]))

    def add_switch_subsys(self, num_actuators, seed):
        connections = self._model.connections.copy()
        for i in range(num_actuators):
            num_pole = random.randint(1, 1)
            connection = random.choice(connections)
            while any('sensor_voltage' in p for p in connection) or any('sensor_both' and 'outport' in p for p in connection):
                connection = random.choice(connections)
            port = random.choice(connection)
            related_connections = self._model.filter_connections([port])
            all_related_connections = [[p for p in related_connections[0] if ('sensor_voltage' not in p)
                                       and ('sensor_both' and 'outport' not in p)]]
            num_connections = random.randint(1, len(all_related_connections[0]))
            while num_connections > 8:
                num_connections = random.randint(1, len(all_related_connections[0]))
            all_related_connections = random.sample(all_related_connections[0], num_connections)
            switchsys = self.create_actuator_subsystem(seed=seed, pole_and_throw=[num_pole, num_connections])
            self._model.add_subsystem(switchsys)
            self._model.add_connection((switchsys.inport_info[0], port))
            i = 0
            for connection in all_related_connections:
                self._model.connections.remove(connection)
                connections.remove(connection)
                remain_port = [x for x in connection if x != port]
                self._model.add_connection((switchsys.outport_info[i], remain_port[0]))
                i += 1

    def build_subsystem(self, max_num_source=3, max_num_sensor=2, max_num_acuator=2, max_num_element=5,
                        max_num_mission=1, mission_name=None, seed=None, battery_sub_exsist=True):
    # def build_subsystem(self, max_num_source=5, max_num_sensor=3, max_num_acuator=2, max_num_element=10, max_num_mission=1, mission_name=None, seed=None):
        if seed:
            random.seed(seed)
        num_sensors = random.randint(1, max_num_sensor)
        num_elements = random.randint(1, max_num_element)
        num_sources = random.randint(1, max_num_source)
        num_actuators = random.randint(1, max_num_acuator)
        num_mission = random.randint(1, max_num_mission)
        for i in range(num_sources):
            if battery_sub_exsist:
                type = random.choice(['voltage', 'current', 'battery'])
            else:
                type = random.choice(['voltage', 'current'])
            subsys = self.create_source_subsystem(type=type, seed=seed)
            self._model.add_subsystem(subsys)
        for i in range(num_elements):
            subsys = self.create_element_subsystem(seed=seed)
            self._model.add_subsystem(subsys)
        num_current_sensor = 0
        for i in range(num_sensors):
            subsys = self.create_sensor_subsystem(seed=seed)
            if subsys.subsystem_type in ['sensor_current', 'sensor_both'] and num_current_sensor < num_elements:
                num_current_sensor += 1
                self._model.add_subsystem(subsys)
            else:
                while subsys.subsystem_type in ['sensor_current', 'sensor_both']:
                    subsys = self.create_sensor_subsystem(seed=seed)
                self._model.add_subsystem(subsys)
        for i in range(num_mission):
            mission_subsys = self.create_mission_subsystem(name=mission_name, seed=seed)
            self._model.add_subsystem(mission_subsys)
        sensor_sys = [subsys for subsys in self._model.subsystem_list if 'sensor' in subsys.subsystem_type]
        element_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'element']
        mission_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'mission']
        source_sys = [subsys for subsys in self._model.subsystem_list if 'source' in subsys.subsystem_type]
        # #biuld base circuit
        element_sys = self.build_base_circuit(element_sys, source_sys[0])
        # add elements
        self.add_element_subsys(element_sys)
        #add mission
        self.add_mission_subsys(mission_sys)
        #add source
        self.add_source_subsys(source_sys)
        #add sensor
        self.add_sensor_subsys(sensor_sys)
        #add switch
        self.add_switch_subsys(num_actuators, seed)

    def random_single_connect(self, component):
        connection = random.choice(self._model.connections)
        port = random.choice(connection)
        self._model.add_connection((port, component.get_port_info()[0]))

    def set_workspace(self):
        i = 0
        for component in self._model.component_list:
            if component.name == 'ToWorkspace':
                component.variable_name = f"simout_{i}"
                i = i + 1
        for subsys in self._model.subsystem_list:
            i = 0
            for component in subsys.component_list:
                if component.name == 'ToWorkspace':
                    component.variable_name = f"{subsys.subsystem_type}_{subsys.ID}_simout_{i}"
                    i = i + 1

    def build_component(self, seed=None):
        if seed:
            random.seed(seed)
        solver = self.component_factory.create_utilities('Solver')
        reference = self.component_factory.create_utilities('Reference')
        self._model.add_component(solver, reference)
        self.random_single_connect(reference)
        self.random_single_connect(solver)


    def build_system(self, max_num_source=3, max_num_sensor=2, max_num_acuator=2, max_num_element=5, max_num_mission=1,
                     mission_name=None, seed=None):
        if seed:
            random.seed(seed)
        self.build_subsystem(max_num_source=max_num_source, max_num_sensor=max_num_sensor, max_num_acuator=max_num_acuator,
                             max_num_element=max_num_element, max_num_mission=max_num_mission, mission_name=mission_name)
        self.build_component()
        self.set_workspace()




class ModelDirector:
    def __init__(self, builder):
        self.builder = builder

    def build_model(self, max_num_source=2, max_num_sensor=2, max_num_acuator=1, max_num_element=3, max_num_mission=1,
                     mission_name=None, seed=None):
        self.builder.build_system(max_num_source=max_num_source, max_num_sensor=max_num_sensor, max_num_acuator=max_num_acuator,
                             max_num_element=max_num_element, max_num_mission=max_num_mission, mission_name=mission_name, seed=seed)
        model = self.builder.product()
        return model


