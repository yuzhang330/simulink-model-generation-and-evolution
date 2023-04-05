#%%
import gin
import random
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

    def get_port_info(self):
        port_info = []
        for port in self.port:
            port_name = f"{self.name}_id{self.ID}_port{port}"
            port_info.append(port_name)
        return port_info

    def take_port(self, value):
        ports = [port_item for port_item in self.get_port_info() if value in port_item]
        return ports

class Workspace(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Workspace", directory, port)
        self.system_type = system_type

class Port(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Port", directory, port)
        self.system_type = system_type

class Utilities(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Utilities", directory, port)
        self.system_type = system_type

class Signal(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Signal", directory, port)
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
#Workspace
class FromWorkspace(Workspace):
    def __init__(self, ID:int=0, data='simin', sample_time:int=0):
        super().__init__('FromWorkspace', ID, 'path', ['1'], 'Common')
        self.data = data
        self.sample_time = sample_time

class ToWorkspace(Workspace):
    def __init__(self, ID:int=0, variable_name='simout', sample_time:int=-1):
        super().__init__('ToWorkspace', ID, 'path', ['1'], 'Common')
        self.variable_name = variable_name
        self.sample_time = sample_time
#Port
class Inport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Inport', ID, 'path', ['1'], 'Common')

class Outport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Outport', ID, 'path', ['1'], 'Common')

class ConnectionPort(Port):
    def __init__(self, ID:int=0, direction='left', port_type=None):
        super().__init__('ConnectionPort', ID, 'path', ['1'], 'Common')
        self.direction = direction
        self.port_type = port_type


#Utilities
class Solver(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Solver', ID, 'path', ['1'], 'Common')

class PSSimuConv(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('PSSimuConv', ID, 'path', ['1','2'], 'Common')

class SimuPSConv(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('SimuPSConv', ID, 'path', ['1','2'], 'Common')

class Scope(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Scope', ID, 'path', ['1'], 'Common')

class Reference(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Reference', ID, 'path', ['1'], 'Both')

#Signal
class Constant(Signal):
    def __init__(self, ID:int=0, value:float=1):
        super().__init__('Constant', ID, 'path', ['1'], 'Common')
        self.value = float(value)

class Step(Signal):
    def __init__(self, ID:int=0, step_time:float=1, initial_value:float=0, final_value:float=1, sample_time:float=0):
        super().__init__('Step', ID, 'path', ['1'], 'Common')
        self.step_time = float(step_time)
        self.initial_value = float(initial_value)
        self.final_value = float(final_value)
        self.sample_time = float(sample_time)

class Sine(Signal):
    def __init__(self, ID:int=0, amplitude:float=1, bias:float=0, frequency:float=1, phase:float=0, sample_time:float=0):
        super().__init__('Sine', ID, 'path', ['1'], 'Common')
        self.amplitude = float(amplitude)
        self.bias = float(bias)
        self.frequency = float(frequency)
        self.phase = float(phase)
        self.sample_time = float(sample_time)


#Actuator
@gin.configurable()
class ElectricalActuator(Actuator):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CircuitBreaker(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5):
        super().__init__('CircuitBreaker', ID, 'path', ['signalLConn1','LConn2','RConn1'], 'Both')
        self.threshold = float(threshold)

@gin.configurable()
class SPSTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5):
        super().__init__('SPSTSwitch', ID, 'path', ['signalLConn1','LConn2','RConn1'], 'Both')
        self.threshold = float(threshold)

@gin.configurable()
class SPDTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5):
        super().__init__('SPDTSwitch', ID, 'path', ['signalLConn1','LConn2','RConn1','RConn2'], 'Both')
        self.threshold = float(threshold)

@gin.configurable()
class SPMTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, number:int=3):
        super().__init__('SPMTSwitch', ID, 'path', ['signalLConn1','LConn2'], 'Both')
        if number < 3:
            self.number = 3
        else:
            self.number = number
        for i in range(self.number):
            self.port.append('RConn' + str(i+1))

    def change_throw_number(self, number):
        self.number = number
        self.port = ['signalLConn1','LConn2']
        for i in range(self.number):
            self.port.append('RConn' + str(i+1))

#Sensor
@gin.configurable()
class ElectricalSensor(Sensor):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CurrentSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('CurrentSensor', ID, 'path', ['scopeLConn1','+LConn2','-RConn1'], 'Both')

@gin.configurable()
class VoltageSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('VoltageSensor', ID, 'path', ['scopeLConn1','+LConn2','-RConn1'], 'Both')

#Source
@gin.configurable()
class ElectricalSource(Source):
    def __init__(self, name, ID, directory, port, current_type, source_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type
        self.source_type = source_type

@gin.configurable()
class Battery(ElectricalSource):
    def __init__(self, ID:int=0, vnom:float=10, innerR:float=10, capacity:float=100):
        super().__init__('Battery', ID, 'path', ['+LConn1','-RConn1'], 'DC', 'battery')
        self.vnom = float(vnom)
        self.innerR = float(innerR)
        self.capacity = float(capacity)

@gin.configurable()
class VoltageSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50, dc_voltage:float=0):
        super().__init__('VoltageSourceAC', ID, 'path', ['+LConn1','-RConn1'], 'AC', 'voltage')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)
        self.dc_voltage = float(dc_voltage)

@gin.configurable()
class ControlledVoltageSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50):
        super().__init__('ControlledVoltageSourceAC', ID, 'path', ['signalLConn1','+LConn2','-RConn1'], 'AC', 'voltage')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)

@gin.configurable()
class CurrentSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50, dc_current:float=0):
        super().__init__('CurrentSourceAC', ID, 'path', ['+LConn1','-RConn1'], 'AC', 'current')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)
        self.dc_current = float(dc_current)

@gin.configurable()
class ControlledCurrentSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50):
        super().__init__('ControlledCurrentSourceAC', ID, 'path', ['signalLConn1','+LConn2','-RConn1'], 'AC', 'current')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)

@gin.configurable()
class VoltageSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, voltage:float=10):
        super().__init__('VoltageSourceDC', ID, 'path', ['+LConn1','-RConn1'], 'DC', 'voltage')
        self.voltage = float(voltage)

@gin.configurable()
class ControlledVoltageSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, voltage:float=10):
        super().__init__('ControlledVoltageSourceDC', ID, 'path', ['signalLConn1','+LConn2','-RConn1'], 'DC', 'voltage')
        self.current = float(voltage)

@gin.configurable()
class CurrentSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, current:float=10):
        super().__init__('CurrentSourceDC', ID, 'path', ['+LConn1','-RConn1'], 'DC', 'current')
        self.current = float(current)

@gin.configurable()
class ControlledCurrentSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, current:float=10):
        super().__init__('ControlledCurrentSourceDC', ID, 'path', ['signalLConn1','+LConn2','-RConn1'], 'DC', 'current')
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
        super().__init__('Capacitor', ID, 'path', ['LConn1','RConn1'], 'AC')
        self.capacitance = float(capacitance)

@gin.configurable()
class VariableCapacitor(ElectricalElement):
    def __init__(self, ID:int=0, Cmin:float=1e-9):
        super().__init__('VariableCapacitor', ID, 'path', ['signalLConn1','LConn2','RConn1'], 'AC')
        self.Cmin = float(Cmin)


@gin.configurable()
class Inductor(ElectricalElement):
    def __init__(self, ID:int=0, inductance:float=10):
        super().__init__('Inductor', ID, 'path', ['LConn1','RConn1'], 'AC')
        self.inductance = float(inductance)

@gin.configurable()
class VariableInductor(ElectricalElement):
    def __init__(self, ID:int=0, Lmin:float=1e-6):
        super().__init__('VariableInductor', ID, 'path', ['signalLConn1','LConn2','RConn1'], 'AC')
        self.Lmin = float(Lmin)

@gin.configurable()
class Resistor(ElectricalElement):
    def __init__(self, ID:int=0, resistance:float=10):
        super().__init__('Resistor', ID, 'path', ['LConn','RConn'], 'Both')
        self.resistance = float(resistance)

@gin.configurable()
class Varistor(ElectricalElement):
    def __init__(self, ID:int=0, vclamp:float=260, roff:float=3e8, ron:float=1, vln:float=130, vnu:float=300, rLeak:float=3e8,
                 alphaNormal:float=45, rUpturn:float=0.07, prm=None):
        super().__init__('Varistor', ID, 'path', ['LConn','RConn'], 'Both')
        if prm:
            if prm not in ['linear', 'power-law']:
                raise ValueError("The 'prm' must be either 'linear' or 'power-law'")
            self.prm = prm
        else:
            self.prm = random.choice(['linear', 'power-law'])

        if self.prm == 'linear':
            self.vclamp = float(vclamp)
            self.roff = float(roff)
            self.ron = float(ron)

        elif self.prm == 'power-law':
            self.vln = float(vln)
            self.vnu = float(vnu)
            self.alphaNormal = float(alphaNormal)
            self.rUpturn = float(rUpturn)
            self.rLeak = float(rLeak)





@gin.configurable()
class Diode(ElectricalElement):
    def __init__(self, ID:int=0, forwardV:float=0.5, onR:float=0.01, breakV:float=500):
        super().__init__('Diode', ID, 'path', ['LConn1','RConn1'], 'AC')
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
# def random_electrical_source(category, current_type, seed=None):
#     if seed:
#         random.seed(seed)
#
#     cls_list= [cls for cls in category.__subclasses__() if cls().current_type == current_type or cls().current_type == 'Both']
#     random_cls = random.choice(cls_list)
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
    # random_cls = random_cls()
    # random_cls.randomize_attributes(seed=seed)
    # return random_cls
#%%
# def create_component(name, category, current_type=None, seed=None):
#     if seed:
#         random.seed(seed)
#
#     for cls in category.__subclasses__():
#         if  cls().name == name:
#             cls_instance = cls()
#             cls_instance.randomize_attributes(seed=seed)
#             if current_type:
#                 if cls().current_type == current_type or cls().current_type == 'Both':
#                     return cls_instance
#                 else:
#                     raise TypeError(f"{name} is not the current type")
#             else:
#                 return cls_instance
#     raise TypeError(f"{name} not found in the category")


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
#%%
# r1 = Resistor()
# r2 = Resistor()
# t = [r1,r2]
# merged_list = [obj.get_port_info() for obj in t]

#%%
# print(('a',t[0].get_port_info()[0]))