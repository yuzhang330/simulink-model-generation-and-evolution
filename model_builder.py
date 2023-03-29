import random
from system import System, Subsystem
from abstract_factory import *

class ModelBuilder:
    def __init__(self, component_factory):
        self.component_factory = component_factory

    def build_component(self):
        pass

    def build_connection(self):
        pass


class ElectricalModelBuilder(ModelBuilder):
    def __init__(self, component_factory):
        super().__init__(component_factory)

    def build_component(self):
        pass

    def build_connection(self):
        pass


class ACBuilder(ElectricalModelBuilder):
    def __init__(self):
        super().__init__(ACComponentFactory())

    def build_component(self):
        print("Building AC component")

    def build_connection(self):
        print("Building AC connection")


class DCBuilder(ElectricalModelBuilder):
    def __init__(self):
        super().__init__(DCComponentFactory())
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
        subsystem_connected.inport = [port_class.ID for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem_connected.outport = [port_class.ID for port_class in subsystem.component_list if
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
        group = [element for element in subsystem.component_list if element.component_type == 'Element']

        # #seperate elements into different groups
        # group_sizes = []
        # while num_components > 0:
        #     rand_num = random.randint(1, num_components)
        #     group_sizes.append(rand_num)
        #     num_components -= rand_num
        # components = subsystem.component_list.copy()
        # groups = []
        # for size in group_sizes:
        #     group = []
        #     for i in range(size):
        #         component = random.choice(components)
        #         group.append(component)
        #         components.remove(component)
        #     groups.append(group)

        #connect components in each group
        #for group in groups:
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
        subsystem.inport = [port_class.ID for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [port_class.ID for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem
    def create_actuator_subsystem(self, seed=None):
        subsystem = Subsystem(subsystem_type='switch')
        if seed:
            random.seed(seed)
        component = self.component_factory.create_actuator(seed=seed)
        subsystem.add_component(component)
        switchs = [switch for switch in subsystem.component_list if switch.component_type == 'Actuator']
        for switch in switchs:
            print(switch.take_port('LConn'))
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
        subsystem.inport = [port_class.ID for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [port_class.ID for port_class in subsystem.component_list if
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
        #connect with ports
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
            subsystem = self.series_connect(subsystem, current_sensors, in_port, [in_port[1]])
            subsystem = self.parallel_connect(subsystem, voltage_sensors, [in_port[1]], out_port)
        elif voltage_sensors:
            subsystem.subsystem_type = 'sensor_voltage'
            subsystem = self.parallel_connect(subsystem, voltage_sensors, in_port, out_port)
        elif current_sensors:
            subsystem.subsystem_type = 'sensor_current'
            subsystem = self.series_connect(subsystem, current_sensors, in_port, out_port)
        subsystem.inport = [port_class.ID for port_class in subsystem.component_list if
                                      port_class.name == 'ConnectionPort' and port_class.port_type == 'Inport']
        subsystem.outport = [port_class.ID for port_class in subsystem.component_list if
                                       port_class.name == 'ConnectionPort' and port_class.port_type == 'Outport']
        return subsystem
    def build_subsystem(self, max_num_source=1, max_num_sensor=3, max_num_acuator=2, max_num_element=3, seed=None):
        if seed:
            random.seed(seed)
        num_sensors = random.randint(1, max_num_sensor)
        num_elements = random.randint(1, max_num_element)
        num_sources = random.randint(1, max_num_source)
        num_actuators = random.randint(1, max_num_acuator)
        for i in range(num_sources):
            type = random.choice(['voltage', 'current', 'battery'])
            subsys = self.create_source_subsystem(type=type)
            self._model.add_subsystem(subsys)
        for i in range(num_elements):
            subsys = self.create_element_subsystem()
            self._model.add_subsystem(subsys)
        for i in range(num_sensors):
            subsys = self.create_sensor_subsystem()
            self._model.add_subsystem(subsys)
        sensor_sys = [subsys for subsys in self._model.subsystem_list if 'sensor' in subsys.subsystem_type]
        element_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'element']
        source_sys = [subsys for subsys in self._model.subsystem_list if subsys.subsystem_type == 'source']
        #biuld base circuit
        subset_size = random.randint(1, len(element_sys))
        parallel_elements = random.sample(element_sys, subset_size)
        for elesys in parallel_elements:
            soursys = source_sys[0]
            for inport in elesys.inport_info:
                self._model.add_connection((inport, soursys.inport_info[0]))
            for outport in elesys.outport_info:
                self._model.add_connection((outport, soursys.outport_info[0]))
            self._model.add_connection()
        element_sys.remove(parallel_elements)
        #take branch elements
        if element_sys:
            subset_size = random.randint(0, (len(source_sys)-1))
            if subset_size <= len(element_sys):
                branch_element = random.sample(element_sys, subset_size)
                element_sys.remove(branch_element)
        # add elements
        while element_sys:
            subset_size = random.randint(1, len(element_sys))
            subset = random.sample(element_sys, subset_size)
            element_sys.remove(subset)
            series_elements_size = random.randint(1, len(subset))
            series_elements = random.sample(element_sys, series_elements_size )
            subset.remove(series_elements)
            #add series elements
            for elesys in series_elements:
                connection = random.choice(self._model.connections)
                self._model.connections.pop(connection)
                if 'source' in connection:
                    s_port = [x for x in connection if 'source' in x]
                    remain_port = [x for x in connection if x != s_port[0]]
                    if 'inport' in s_port[0]:
                        for inport in elesys.inport_info:
                            self._model.add_connection((inport, s_port[0]))
                        for outport in elesys.outport_info:
                            self._model.add_connection((outport, remain_port))
                    if 'outport' in s_port[0]:
                        for inport in elesys.inport_info:
                            self._model.add_connection((inport, remain_port))
                        for outport in elesys.outport_info:
                            self._model.add_connection((outport, s_port[0]))
                else:
                        if 'inport' in connection[0]:
                            for inport in elesys.inport_info:
                                self._model.add_connection((inport, connection[1]))
                            for outport in elesys.outport_info:
                                self._model.add_connection((outport, connection[0]))
                        else:
                            for inport in elesys.inport_info:
                                self._model.add_connection((inport, connection[0]))
                            for outport in elesys.outport_info:
                                self._model.add_connection((outport, connection[1]))
            #add parallel elements
            if subset:
                for elesys in subset:
                    connections = self._model.connections.copy()
                    port_1 = 'p'
                    while 'inport' not in port_1 or 'source' in port_1:
                        connection_1 = random.choice(connections)
                        port_1 = random.choice(connection_1)
                    for inport in elesys.inport_info:
                        self._model.add_connection((inport, port_1))
                    port_2 = 'p'
                    while 'outport' not in port_2 or 'source' in port_2 or port_2 in connection_1:
                        connection = random.choice(connections)
                        port_2 = random.choice(connection)
                    for outport in elesys.outport_info:
                        self._model.add_connection((outport, port_2))
            #add source
            exclude_ports = self._model.extract_elements([source_sys[0].inport_info[0], source_sys[0].outport_info[0]])
            path = self._model.find_paths(source_sys[0].inport_info[0], source_sys[0].outport_info[0])
            exclude_paths = [path]
            for soursys in source_sys[1:]:
                type = random.choice(['s','p'])
                if type == 'p':
                    connections = self._model.connections.copy()
                    port_1 = source_sys[0].inport_info[0]
                    port_2 = source_sys[0].outport_info[0]
                    while any(port_1 in sublist for sublist in exclude_ports) and any(port_2 in sublist
                                                                                      for sublist in exclude_ports):
                        while 'inport' not in port_1 or port_1:
                            connection_1 = random.choice(connections)
                            port_1 = random.choice(connection_1)
                        while 'outport' not in port_2  or port_2 in connection_1:
                            connection = random.choice(connections)
                            port_2 = random.choice(connection)
                    for inport in soursys.inport_info:
                        self._model.add_connection((inport, port_1))
                    for outport in soursys.outport_info:
                        self._model.add_connection((outport, port_2))
                    exclude_ports.append(self._model.extract_elements([soursys.inport_info[0], soursys.outport_info[0]]))
                if type == 's':
                    connection = random.choice(self._model.connections)
                    if any(connection in sublist for sublist in path):
                        if len(path) > 1:
                            path = [sublist for sublist in path if connection not in path]
                    while any(connection in sublist for sublist in path) and len(path) == 1:
                        connection = random.choice(self._model.connections)
                    self._model.connections.pop(connection)
                    if 'source' in connection:
                        s_port = [x for x in connection if 'source' in x]
                        remain_port = [x for x in connection if x != s_port[0]]
                        if 'inport' in s_port[0]:
                            for inport in soursys.inport_info:
                                self._model.add_connection((inport, remain_port))
                            for outport in soursys.outport_info:
                                self._model.add_connection((outport, s_port[0]))
                        if 'outport' in s_port[0]:
                            for inport in soursys.inport_info:
                                self._model.add_connection((inport, s_port[0]))
                            for outport in soursys.outport_info:
                                self._model.add_connection((outport, remain_port))
                    else:
                        if 'inport' in connection[0]:
                            for inport in soursys.inport_info:
                                self._model.add_connection((inport, connection[0]))
                            for outport in soursys.outport_info:
                                self._model.add_connection((outport, connection[1]))
                        else:
                            for inport in soursys.inport_info:
                                self._model.add_connection((inport, connection[1]))
                            for outport in soursys.outport_info:
                                self._model.add_connection((outport, connection[0]))
                    exclude_paths.append(self._model.find_paths(soursys[0].inport_info[0],
                                                                soursys[0].outport_info[0]))





















        # connect sensor_sys with element_sys
        element_sys_copy = element_sys.copy()
        for sensys in sensor_sys:
            sensys.list_ports()
            if element_sys_copy:
                if sensys.subsystem_type == 'sensor_voltage':
                    elesys = random.choice(element_sys_copy)
                    elesys.list_ports()
                    self._model.add_connection((random.choice(sensys.inport_info),random.choice(elesys.inport_info)),
                                               (random.choice(sensys.outport_info),random.choice(elesys.outport_info)))



    def build_component(self):
        print("Building DC component")

    def build_connection(self):
        print("Building DC connection")


class ElectricalModelDirector:
    def __init__(self, builder):
        self.builder = builder

    def build_acmodel(self):
        self.builder.build_component()
        self.builder.build_connection()

    def build_dcmodel(self):
        self.builder.build_component()
        self.builder.build_connection()