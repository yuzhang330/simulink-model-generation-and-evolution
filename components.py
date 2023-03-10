#%%
import gin

@gin.configurable()
class Component:
    def __init__(self, name, ID, component_type, directory, port):
        self.port = port
        self.name = name
        self.ID = ID
        self.component_type = component_type
        self.directory = directory

    def change_parameter(self, parameter_name, value):
        if hasattr(self, parameter_name):
            setattr(self, parameter_name, value)
        else:
            raise ValueError(f"{parameter_name} is not a valid parameter.")

    def list_attributes(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}

    @gin.configurable()
    def randomize_attributes(self, range=[0.5,1.5], seed=None):
        if seed:
            random.seed(seed)
        attributes = self.list_attributes()
        for attr, default_value in attributes.items():
            if not isinstance(default_value, (int, float)):
                continue
            value_range = (range[0] * default_value, range[1] * default_value)
            if isinstance(default_value, int):
                new_value = random.randint(int(value_range[0]), int(value_range[1]))
            else:
                new_value = random.uniform(value_range[0], value_range[1])
            setattr(self, attr, new_value)


class Port(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Port", directory, port)
        self.system_type = system_type

@gin.configurable()
class Element(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Element", directory, port)
        self.system_type = system_type

@gin.configurable()
class Source(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Source", directory, port)
        self.system_type = system_type

@gin.configurable()
class Sensor(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Sensor", directory, port)
        self.system_type = system_type

@gin.configurable()
class Actuator(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Actuator", directory, port)
        self.system_type = system_type

#Port
class Inport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Inport', ID, 'path', [1], 'Common')

class Outport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Outport', ID, 'path', [1], 'Common')

#Actuator
@gin.configurable()
class ElectricalActuator(Actuator):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CircuitBreaker(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=10):
        super().__init__('CircuitBreaker', ID, 'path', [], 'Both')
        self.threshold = float(threshold)

@gin.configurable()
class SPDTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=10):
        super().__init__('SPDTSwitch', ID, 'path', [], 'Both')
        self.threshold = float(threshold)

@gin.configurable()
class SPMTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, number:int=3):
        super().__init__('SPMTSwitch', ID, 'path', [], 'Both')
        self.number = number

#Sensor
@gin.configurable()
class ElectricalSensor(Sensor):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CurrentSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('CurrentSensor', ID, 'path', [], 'Both')

@gin.configurable()
class VoltageSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('VoltageSensor', ID, 'path', [], 'Both')

#Source
@gin.configurable()
class ElectricalSource(Source):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class Battery(ElectricalSource):
    def __init__(self, ID:int=0, vnom:float=10, innerR:float=10, capacity:float=100):
        super().__init__('Battery', ID, 'path', [], 'DC')
        self.vnom = float(vnom)
        self.innerR = float(innerR)
        self.capacity = float(capacity)

@gin.configurable()
class VoltageSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50):
        super().__init__('VoltageSourceAC', ID, 'path', [], 'AC')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)

@gin.configurable()
class CurrentSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50):
        super().__init__('CurrentSourceAC', ID, 'path', [], 'AC')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)

@gin.configurable()
class VoltageSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, voltage:float=10):
        super().__init__('VoltageSourceDC', ID, 'path', [], 'DC')
        self.voltage = float(voltage)

@gin.configurable()
class CurrentSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, current:float=10):
        super().__init__('CurrentSourceDC', ID, 'path', [], 'DC')
        self.current = float(current)

#Element
@gin.configurable()
class ElectricalElement(Element):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class Capacitor(ElectricalElement):
    def __init__(self, ID:int=0, capacitance:float=10):
        super().__init__('Capacitor', ID, 'path', [], 'AC')
        self.capacitance = float(capacitance)

@gin.configurable()
class Inductor(ElectricalElement):
    def __init__(self, ID:int=0, inductance:float=10):
        super().__init__('Inductor', ID, 'path', [], 'AC')
        self.inductance = float(inductance)

@gin.configurable()
class Resistor(ElectricalElement):
    def __init__(self, ID:int=0, resistance:float=10):
        super().__init__('Resistor', ID, 'path', [], 'Both')
        self.resistance = float(resistance)

@gin.configurable()
class Reference(ElectricalElement):
    def __init__(self, ID:int=0):
        super().__init__('Reference', ID, 'path', [], 'Both')

@gin.configurable()
class Diode(ElectricalElement):
    def __init__(self, ID:int=0, forwardV:float=0.5, onR:float=0.01, breakV:float=500):
        super().__init__('Diode', ID, 'path', [], 'Both')
        self.forwardV = float(forwardV)
        self.onR = float(onR)
        self.breakV = float(breakV)

#%%
###################################
# import random
# import inspect
# import sys
#
# def get_random_ac_source():
#     candidates = []
#     for name, obj in inspect.getmembers(sys.modules[__name__]):
#         if inspect.isclass(obj) and issubclass(obj, Electrical_Source) and obj != Electrical_Source:
#             objinstance = obj()
#             if objinstance.current_type == 'AC':
#                 candidates.append(obj)
#     random_class = random.choice(candidates)
#     sig = inspect.signature(random_class.__init__)
#     args = {}
#     for name, param in sig.parameters.items():
#         if name != 'self':
#             default_value = param.default
#             if isinstance(default_value, int):
#                 random_value = random.randint(int(default_value*0.5), int(default_value*1.5))
#             elif isinstance(default_value, float):
#                 random_value = random.uniform(default_value*0.5, default_value*1.5)
#             else:
#                 random_value = default_value
#             args[name] = random_value
#     return random_class(**args)
#%%
# a = get_random_ac_source()
# a = Battery()
#%%
# print(a.name)
#%%
def random_electrical_source(category, current_type, seed=None):
    if seed:
        random.seed(seed)

    cls_list= [cls for cls in category.__subclasses__() if cls().current_type == current_type or cls().current_type == 'Both']
    random_cls = random.choice(cls_list)
    # sig = inspect.signature(random_cls.__init__)
    # Get the default values of each argument
    # default_args = {
    #     name: param.default
    #     for name, param in sig.parameters.items()
    #     if param.default is not inspect.Parameter.empty
    # }
    # kwargs = {}
    # for key, value in default_args.items():
    #     if type(value) is int:
    #         kwargs[key] = int(random.uniform(0.5, 1.5) * value)
    #     elif type(value) is float:
    #         kwargs[key] = random.uniform(0.5, 1.5) * value
    #     else:
    #         kwargs[key] = value
    random_cls = random_cls()
    random_cls.randomize_attributes(seed=seed)
    return random_cls
#%%
def create_component(name, category, current_type=None, seed=None):
    if seed:
        random.seed(seed)

    for cls in category.__subclasses__():
        if  cls().name == name:
            cls_instance = cls()
            cls_instance.randomize_attributes(seed=seed)
            if current_type:
                if cls().current_type == current_type or cls().current_type == 'Both':
                    return cls_instance
                else:
                    raise TypeError(f"{name} is not the current type")
            else:
                return cls_instance
    raise TypeError(f"{name} not found in the category")


#%%
# b = random_electrical_source(Electrical_Element, 'DC')
# b.list_attributes()
#%%
# b.change_parameter('peak',100)
# b.randomize_attributes(seed=11)
# b.list_attributes()
#%%
# c = create_component('Inductor', Electrical_Element, current_type='AC', seed=1)
# c.list_attributes()