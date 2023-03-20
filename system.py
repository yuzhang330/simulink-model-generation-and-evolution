from components import Component
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

    def add_connection(self, connection):
        if isinstance(connection, tuple):
            self.connections.append(connection)
        else:
            raise ValueError("Connections must be tuples.")

    def list_components(self):
        return [f"{component.name}_id{component.ID}" for component in self.component_list]

    def list_connections(self):
        return [f"{src} -> {dest}" for (src, dest) in self.connections]


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

    def add_subsystem(self, subsystem):
        if isinstance(subsystem, Subsystem):
            self.subsystem_list.append(subsystem)
        else:
            raise ValueError("Only instances of Subsystem can be added to the subsystem_list.")

    def add_connection(self, connection):
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
