from components import *

class Container:
    def __init__(self, inport, outport):
        self.inport = inport
        self.outport = outport

    def change_parameter(self, parameter_name, value):
        if hasattr(self, parameter_name):
            setattr(self, parameter_name, value)
        else:
            raise ValueError(f"{parameter_name} is not a valid parameter.")


class Subsystem(Container):
    def __init__(self, inport=[], outport=[], name='subsystem', ID=0, subsystem_type=None):
        super().__init__(inport, outport)
        self.component_list = []
        self.connections = []
        self.name = name
        self.ID = ID
        self.subsystem_type = subsystem_type
        self.inport_info = []
        self.outport_info = []

    def add_component(self, *components):
        for component in components:
            if isinstance(component, Component):
                name_count = sum(1 for c in self.component_list if c.name == component.name)
                if name_count > 0:
                    existing_ids = [c.ID for c in self.component_list if c.name == component.name]
                    max_id = max(existing_ids)
                    component.ID = max_id + 1
                self.component_list.append(component)
            else:
                raise ValueError("Only instances of Component can be added to component_list.")

    def add_connection(self, *connections):
        for connection in connections:
            if isinstance(connection, tuple):
                self.connections.append(connection)
            else:
                raise ValueError("Connections must be tuples.")

    def list_components(self):
        return [f"{component.name}_id{component.ID}" for component in self.component_list]

    def list_connections(self):
        return [f"{src} -> {dest}" for (src, dest) in self.connections]

    def list_ports(self):
        for port in self.inport:
            port_name = f"{self.name}_{self.subsystem_type }_id{self.ID}_inport{port}"
            self.inport_info.append(port_name)
        for port in self.outport:
            port_name = f"{self.name}_{self.subsystem_type }_id{self.ID}_outport{port}"
            self.outport_info.append(port_name)

    def change_component_paramter(self, parameter_name, parameter_value, component_name, component_id):
        for component in self.component_list:
            if component.name == component_name and component.ID == component_id:
                new_component = component
                self.component_list.remove(component)
                if hasattr(new_component, parameter_name):
                    setattr(new_component, parameter_name, parameter_value)
                self.component_list.append(new_component)

    def list_played_components(self):
        played_ports = [port.replace('signal', '') for instance in self.component_list for port in instance.get_port_info() if 'signal' in port]
        adjacent_ports = []
        for element in played_ports:
            for tup in self.connections:
                if element in tup:
                    index = tup.index(element)
                    adjacent_ports.append(tup[1 - index])
                    break
        connections = []
        for element in adjacent_ports:
            element = '_'.join(element.split('_', 2)[:2])
            temp = []
            for tup in self.connections:
                p_list = [p for p in tup if element in p]
                if p_list:
                    index = tup.index(p_list[0])
                    temp.append(tup[1 - index])
            if len(temp) >= 2:
                connections.append(temp)
        played_components = []
        for connection in connections:
            played_couple = []
            for element in connection:
                name, id_str, _ = element.split('_', 2)
                id = int(id_str[2:])
                for component in self.component_list:
                    if component.name == name and component.ID == id:
                        played_couple.append(component)
            played_components.append(played_couple)
        return played_components

    def change_signal(self, name, id, new_name):
        signal = [instance for instance in self.component_list if instance.name == name and instance.ID == id
                  and instance.component_type == 'Signal']
        if not signal:
            raise ValueError("There is no such signal component in the system.")
        else:
            index_list = [i for i, instance in enumerate(self.component_list) if instance == signal[0]]
            found = False
            for cls in Signal.__subclasses__():
                if cls().name == new_name:
                    new_signal = cls()
                    if len(new_signal.port) == len(signal[0].port):
                        self.add_component(new_signal)
                        new_connections = []
                        old_ports_map = dict(zip(signal[0].get_port_info(), new_signal.get_port_info()))
                        for pair in self.connections:
                            first_element = pair[0] if pair[0] not in old_ports_map else old_ports_map[pair[0]]
                            second_element = pair[1] if pair[1] not in old_ports_map else old_ports_map[pair[1]]
                            new_connections.append((first_element, second_element))
                        self.connections = new_connections
                        self.component_list.pop(index_list[0])
                        found = True
                    else:
                        raise ValueError("The number of ports do not match.")
            if not found:
                raise ValueError("There is no such new signal component.")

    def change_workspace(self, id, variable_name):
        found = False
        for instance in self.component_list:
            if instance.name == 'FromWorkspace' and instance.ID == id:
                instance.variable_name = variable_name
                found = True
        if not found:
            raise ValueError("There is no such FromWorkspace component.")

class System(Container):
    def __init__(self, inport=[], outport=[], solver='ode45', stop_time=100):
        super().__init__(inport, outport)
        self.component_list = []
        self.subsystem_list = []
        self.connections = []
        self.solver = solver
        self.stop_time = stop_time

    def add_component(self, *components):
        for component in components:
            if isinstance(component, Component):
                name_count = sum(1 for c in self.component_list if c.name == component.name)
                if name_count > 0:
                    existing_ids = [c.ID for c in self.component_list if c.name == component.name]
                    max_id = max(existing_ids)
                    component.ID = max_id + 1
                self.component_list.append(component)
            else:
                raise ValueError("Only instances of Component can be added to component_list.")

    def add_subsystem(self, *subsystems):
        for subsystem in subsystems:
            if isinstance(subsystem, Subsystem):
                name_count = sum(1 for s in self.subsystem_list if s.subsystem_type == subsystem.subsystem_type)
                if name_count > 0:
                    existing_ids = [sub.ID for sub in self.subsystem_list]
                    max_id = max(existing_ids)
                    subsystem.ID = max_id + 1
                subsystem.list_ports()
                self.subsystem_list.append(subsystem)
            else:
                raise ValueError("Only instances of Subsystem can be added to the subsystem_list.")

    def add_connection(self, *connections):
        for connection in connections:
            if isinstance(connection, tuple):
                self.connections.append(connection)
            else:
                raise ValueError("Connections must be tuples.")

    def list_components(self):
        return [f"{component.name}_id{component.ID}" for component in self.component_list]

    def list_subsystem(self):
        return [subsystem.name for subsystem in self.subsystem_list]

    def list_connections(self):
        return [f"{src} -> {dest}" for (src, dest) in self.connections]

    def change_component_paramter(self, parameter_name, parameter_value, component_name, component_id,
                                  subsystem_type=None, subsystem_id=None):
        if subsystem_type and subsystem_id is not None:
            for subsys in self.subsystem_list:
                if subsys.subsystem_type == subsystem_type and subsys.ID == subsystem_id:
                    new_subsys = subsys
                    self.subsystem_list.remove(subsys)
                    for component in new_subsys.component_list:
                        if component.name == component_name and component.ID == component_id:
                            new_component = component
                            new_subsys.component_list.remove(component)
                            if hasattr(new_component, parameter_name):
                                setattr(new_component, parameter_name, parameter_value)
                            new_subsys.component_list.append(new_component)
                    self.subsystem_list.append(new_subsys)
        else:
            for component in self.component_list:
                if component.name == component_name and component.ID == component_id:
                    new_component = component
                    self.component_list.remove(component)
                    if hasattr(new_component, parameter_name):
                        setattr(new_component, parameter_name, parameter_value)
                    self.component_list.append(new_component)

    def list_played_components(self):
        played_ports = [port.replace('signal', '') for instance in self.component_list for port in instance.get_port_info() if 'signal' in port]
        adjacent_ports = []
        for element in played_ports:
            for tup in self.connections:
                if element in tup:
                    index = tup.index(element)
                    adjacent_ports.append(tup[1 - index])
                    break
        connections = []
        for element in adjacent_ports:
            element = '_'.join(element.split('_', 2)[:2])
            temp = []
            for tup in self.connections:
                p_list = [p for p in tup if element in p]
                if p_list:
                    index = tup.index(p_list[0])
                    temp.append(tup[1 - index])
            if len(temp) >= 2:
                connections.append(temp)
        played_components = []
        for connection in connections:
            played_couple = []
            for element in connection:
                name, id_str, _ = element.split('_', 2)
                id = int(id_str[2:])
                for component in self.component_list:
                    if component.name == name and component.ID == id:
                        played_couple.append(component)
            played_components.append(played_couple)
        return played_components

    def list_all_played_component(self):
        played_dic = {}
        for subsys in self.subsystem_list:
            played_dic[f'subsystem_{subsys.subsystem_type}_{subsys.ID}'] = subsys.list_played_components()
        played_dic['system'] = self.list_played_components()
        return played_dic


    def remove_after_last_underscore(self, s):
        last_underscore_index = s.rfind('_')
        if last_underscore_index != -1:
            return s[:last_underscore_index]
        return s

    def remove_substring_after_id(self, input_string):
        id_index = input_string.find('id')
        underscore_index = input_string.find('_', id_index)
        return input_string[:underscore_index]

    def find_paths(self, start, end):
        def path(visited, visited_nodes, current):
            if current == end:
                result.append(visited)
                return
            current_new = self.remove_substring_after_id(current)
            for pair in self.connections:
                new_pair = (self.remove_substring_after_id(pair[0]), self.remove_substring_after_id(pair[1]))
                if current_new in new_pair:
                    old_node = pair[0] if new_pair[0] == current_new else pair[1]
                    if old_node != end:
                        next_node = pair[0] if new_pair[1] == current_new else pair[1]
                        next_node_new = self.remove_substring_after_id(next_node)
                        if pair not in visited and next_node_new not in visited_nodes:
                            path(visited + [pair], visited_nodes | {next_node_new}, next_node)

        result = []
        path([], {start}, start)
        return result

    def extract_elements(self, elements, connections=None):
        if connections:
            connection_list = connections
        else:
            connection_list = self.connections
        result = [[] for _ in range(len(elements))]
        visited = set()
        def chain(start, index):
            visited.add(start)
            result[index].append(start)
            # for t in self.connections:
            for t in connection_list:
                if start in t:
                    next_node = t[0] if t[1] == start else t[1]
                    if next_node not in visited:
                        print('port')
                        chain(next_node, index)
        for i, element in enumerate(elements):
            chain(element, i)
        print('portre')
        return result

    def filter_connections(self, port_list):
        result = []
        for element in port_list:
            filter_connections = [t for t in self.connections if element in t]
            result.append(filter_connections)
        return result

