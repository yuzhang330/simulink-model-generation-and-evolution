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
    def __init__(self, inport=[], outport=[], name='subsytem', ID=0, subsystem_type=None):
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

    def change_workspace(self, id, new_data):
        found = False
        for instance in self.component_list:
            if instance.name == 'FromWorkspace' and instance.ID == id:
                instance.data = new_data
                found = True
        if not found:
            raise ValueError("There is no such FromWorkspace component.")

class System(Container):
    def __init__(self, inport=[], outport=[], solver='ode', stop_time=1000):
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

    def list_played_components(self):
        played_ports = [port.replace('signal', '') for instance in self.component_list for port in instance.get_port_info() if 'signal' in port]
        print(played_ports)
        adjacent_ports = []
        for element in played_ports:
            for tup in self.connections:
                if element in tup:
                    index = tup.index(element)
                    adjacent_ports.append(tup[1 - index])
                    break
        print(adjacent_ports)
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

    def remove_after_third_underscore(s):
        count = 0
        for i, char in enumerate(s):
            if char == '_':
                count += 1
                if count == 3:
                    return s[:i]
        return s
    def find_paths(self, start, end):
        def path(visited, current):
            if current == end:
                result.append(visited)
                return

            for pair in self.connections:
                new_pair = (self.remove_after_third_underscore(pair[0]),self.remove_after_third_underscore(pair[1]))
                if current in new_pair:
                    next_node = new_pair[0] if new_pair[1] == current else new_pair[1]
                    if pair not in visited:
                        path(visited + [pair], next_node)

        result = []
        path([], start)
        return result

    def extract_elements(self, elements):
        result = [[] for _ in range(len(elements))]
        visited = set()
        def chain(start, index):
            visited.add(start)
            result[index].append(start)
            for t in self.connections:
                if start in t:
                    next_node = t[0] if t[1] == start else t[1]
                    if next_node not in visited:
                        chain(next_node, index)
        for i, element in enumerate(elements):
            chain(element, i)
        return result

