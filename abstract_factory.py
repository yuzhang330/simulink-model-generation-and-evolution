import random
# import inspect
# import sys
import gin
#%%
from components import *
#%%
class AbstractComponentFactory:

    def create_sensor(self, name):
        pass

    def create_source(self, name):
        pass

    def create_element(self, name):
        pass

    def create_actuator(self, name):
        pass

    def create_port(self, name):
        pass

    def create_utilities(self, name):
        pass

    def create_signal(self, name):
        pass


class ElectriaclComponentFactory(AbstractComponentFactory):
    def create_component(self, name, category, current_type=None, seed=None, randomattr=True):
        for cls in category.__subclasses__():
            if cls().name == name:
                cls_instance = cls()
                if randomattr:
                    cls_instance.randomize_attributes(seed=seed)
                if current_type:
                    if cls().current_type == current_type or cls().current_type == 'Both':
                        return cls_instance
                    else:
                        raise TypeError(f"{name} is not the current type")
                else:
                    return cls_instance
        raise TypeError(f"{name} not found in the category")

    def random_component(self, category, current_type=None, seed=None):
        if seed:
            random.seed(seed)
        cls_list = [cls for cls in category.__subclasses__() if current_type is None
                    or cls().current_type == current_type or cls().current_type == 'Both']
        random_cls = random.choice(cls_list)
        random_cls_instance = random_cls()
        random_cls_instance.randomize_attributes(seed=seed)
        return random_cls_instance

    @gin.configurable()
    def create_sensor(self, name):
        pass

    @gin.configurable()
    def create_source(self, name):
        pass

    @gin.configurable()
    def create_element(self, name):
        pass

    @gin.configurable()
    def create_actuator(self, name):
        pass

    def create_port(self, name, type=None):
        if type == 'electrical':
            port = self.create_component('ConnectionPort', Port, randomattr=False)
            if name == 'Inport':
                port.port_type = 'Inport'
            if name == 'Outport':
                port.port_type = 'Outport'
                port.direction = 'right'
            return port
        else:
            return self.create_component(name, Port, randomattr=False)

    def create_utilities(self, name):
        return self.create_component(name, Utilities, randomattr=False)

    @gin.configurable()
    def create_signal(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, Signal, seed=seed, randomattr=randomattr)
        else:
            return self.random_component(Signal, seed=seed)

    @gin.configurable()
    def create_workspace(self, name):
        return self.create_component(name, Workspace, randomattr=False)

@gin.configurable()
class ACComponentFactory(ElectriaclComponentFactory):

    def create_sensor(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalSensor, current_type='AC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalSensor, 'AC', seed=seed)


    def create_source(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalSource, current_type='AC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalSource, 'AC', seed=seed)


    def create_element(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalElement, current_type='AC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalElement, 'AC', seed=seed)


    def create_actuator(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalActuator, current_type='AC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalActuator, 'AC', seed=seed)

@gin.configurable()
class DCComponentFactory(ElectriaclComponentFactory):

    def create_sensor(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalSensor, current_type='DC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalSensor, 'DC', seed=seed)


    def create_source(self, name=None, type=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalSource, current_type='DC', seed=seed, randomattr=randomattr)
        elif type:
            if seed:
                random.seed(seed)
            cls_list = [cls for cls in ElectricalSource.__subclasses__() if cls().source_type == type
                        and (cls().current_type == 'DC' or cls().current_type == 'Both')]
            random_cls = random.choice(cls_list)
            random_cls_instance = random_cls()
            random_cls_instance.randomize_attributes(seed=seed)
            return random_cls_instance
        else:
            return self.random_component(ElectricalSource, 'DC', seed=seed)


    def create_element(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalElement, current_type='DC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalElement, 'DC', seed=seed)


    def create_actuator(self, name=None, seed=None, randomattr=True):
        if name:
            return self.create_component(name, ElectricalActuator, current_type='DC', seed=seed, randomattr=randomattr)
        else:
            return self.random_component(ElectricalActuator, 'DC', seed=seed)
#%%
# gin.parse_config_file('my_config.gin')
# a = DCComponentFactory()
# ele = a.create_source('Battery',randomattr=False)
#%%
# ele.list_attributes()
#%%
# sour = a.create_element('Varistor')