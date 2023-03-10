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

    def create_source_subsystem(self):
        return

    def create_element_subsystem(self, max_num_component=5, seed=None):
        subsystem = Subsystem()
        #create elements randomly
        num_components = random.randint(1, max_num_component)
        for i in range(num_components):
            component = self.component_factory.create_element(seed)
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
        #create ports for each group
        for i in range(len(groups)):
            inport = self.component_factory.create_port('Inport')
            subsystem.add_component(inport)
            outport = self.component_factory.create_port('Outport')
            subsystem.add_component(outport)
        return subsystem
    def create_actuator_subsystem(self):
        return
    def create_sensor_subsystem(self):
        return
    def create_subsystem(self):
        subsystem = Subsystem()
        return subsystem

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