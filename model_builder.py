import random
from system import System,Subsystem
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

    def series_connect(self, subsys, component_type):
        subsystem = subsys
        comp = [comp for comp in subsystem.component_list if comp.component_type == component_type]
        in_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Outport']
        comp_port = [obj.get_port_info() for obj in comp]
        for i in range(len(comp_port) - 1):
            list_positive = [elem for elem in comp_port[i] if '+' in elem]
            list_negative = [elem for elem in comp_port[i + 1] if '-' in elem]
            if i == 0:
                subsystem.add_connection((list_positive[0].replace('+', ''), in_port[0].get_port_info()[0]))
            if i == len(comp_port) - 2:
                subsystem.add_connection((list_negative[0].replace('-', ''), out_port[0].get_port_info()[0]))
            new_connect = (list_positive[0].replace('+', ''), list_negative[0].replace('-', ''))
            subsystem.add_connection(new_connect)
        return subsystem

    def parallel_connect(self, subsys, component_type):
        subsystem = subsys
        comp = [comp for comp in subsystem.component_list if comp.component_type == component_type]
        in_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Inport']
        out_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Outport']
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
                    name = random.choice(['VoltageSourceDC','Battery'])
                    component = self.component_factory.create_source(name=name,seed=seed)
                else:
                    component = self.component_factory.create_source(name='VoltageSourceDC',seed=seed)
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport')
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(inport, outport)
            # connect with ports
            subsystem_connected = self.series_connect(subsystem, 'Source')
        if type == 'current':
            subsystem = Subsystem(subsystem_type='source_current')
            num_sources = random.randint(1, max_num_component)
            for i in range(num_sources):
                component = self.component_factory.create_source(name='CurrentSourceDC',seed=seed)
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport')
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(inport, outport)
            # connect with ports
            subsystem_connected = self.parallel_connect(subsystem, 'Source')
        if type == 'battery':
            subsystem = Subsystem(subsystem_type='source_battery')
            num_sources = random.randint(1, max_num_component)
            seed_b = random.randint(1, 100)
            for i in range(num_sources):
                component = self.component_factory.create_source(name='Battery',seed=seed_b)
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport')
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(inport, outport)
            type_b = random.choice(['s','p'])
            if type_b == 's':
                subsystem_connected = self.series_connect(subsystem,'Source')
            if type_b == 'p':
                subsystem_connected = self.parallel_connect(subsystem,'Source')


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
        #seperate elements into different groups
        group_sizes = []
        while num_components > 0:
            rand_num = random.randint(1, num_components)
            group_sizes.append(rand_num)
            num_components -= rand_num
        components = subsystem.component_list.copy()
        groups = []
        for size in group_sizes:
            group = []
            for i in range(size):
                component = random.choice(components)
                group.append(component)
                components.remove(component)
            groups.append(group)
        #connect components in each group
        for group in groups:
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
                inport = self.component_factory.create_port('Inport')
                outport = self.component_factory.create_port('Outport')
                subsystem.add_component(inport,outport)
                n = random.randint(0, len(unused_port)-2)
                for i in range(n):
                    port_name = random.choice(['Inport','Outport'])
                    port = self.component_factory.create_port(port_name)
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

        return subsystem
    def create_actuator_subsystem(self):
        return
    def create_sensor_subsystem(self, type, max_num_component=3, seed=None):
        if seed:
            random.seed(seed)
        if type == 'voltage':
            subsystem = Subsystem(subsystem_type='sensor_voltage')
            num_sensors = random.randint(1, max_num_component)
            for i in range(num_sensors):
                component = self.component_factory.create_sensor(name='VoltageSensor')
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport')
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(inport,outport)
            #connect with ports
            sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
            in_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Outport']
            for sensor in sensors:
                for port in sensor.get_port_info():
                    if '+' in port:
                        subsystem.add_connection((port.replace('+', ''),in_port[0].get_port_info()[0]))
                    if '-' in port:
                        subsystem.add_connection((port.replace('-', ''),out_port[0].get_port_info()[0]))

        if type == 'current':
            subsystem = Subsystem(subsystem_type='sensor_current')
            num_sensors = random.randint(1, max_num_component)
            for i in range(num_sensors):
                component = self.component_factory.create_sensor(name='CurrentSensor')
                subsystem.add_component(component)
            inport = self.component_factory.create_port('Inport')
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(inport,outport)
            #connect with ports
            sensors = [sensor for sensor in subsystem.component_list if sensor.component_type == 'Sensor']
            in_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Inport']
            out_port = [port_class for port_class in subsystem.component_list if port_class.name == 'Outport']
            sensors_port = [obj.get_port_info() for obj in sensors]
            for i in range(len(sensors_port) - 1):
                list_positive = [elem for elem in sensors_port[i] if '+' in elem]
                list_negative = [elem for elem in sensors_port[i + 1] if '-' in elem]
                if i == 0:
                    subsystem.add_connection((list_positive[0].replace('+', ''), in_port[0].get_port_info()[0]))
                if i == len(sensors_port) - 2:
                    subsystem.add_connection((list_negative[0].replace('-', ''), out_port[0].get_port_info()[0]))
                new_connect = (list_positive[0].replace('+', ''), list_negative[0].replace('-', ''))
                subsystem.add_connection(new_connect)
        return subsystem
    def build_subsystem(self):
        subsystem = Subsystem()


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