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

    @property
    def parameter(self):
        parameters = {
        }
        return parameters

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

    def take_port(self, string):
        ports = [port_item for port_item in self.get_port_info() if string in port_item]
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

@gin.configurable()
class Mission(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Mission", directory, port)
        self.system_type = system_type

@gin.configurable()
class Logic(Component):
    def __init__(self, name, ID, directory, port, system_type):
        super().__init__(name, ID, "Logic", directory, port)
        self.system_type = system_type

#Logic
class Comparator(Logic):
    def __init__(self, ID:int=0):
        super().__init__('Comparator', ID, 'simulink/Quick Insert/Logic and Bit Operations/Equal', ['IN1', 'IN2', 'OUT1'], 'Common')



class Voter(Logic):
    def __init__(self, ID:int=0):
        super().__init__('Voter', ID, 'simulink/User-Defined Functions/MATLAB Function', ['IN1', 'OUT1'], 'Common')
        self.voter = """function y = voter(u)
                        u = u(~isnan(u));
                        y = mode(u);
                        end
                        """
    @property
    def parameter(self):
        parameters = {
            'Function': self.voter
        }
        return parameters

class Sparing(Logic):
    def __init__(self, ID:int=0, n:int=1):
        super().__init__('Sparing', ID, 'simulink/User-Defined Functions/MATLAB Function', ['IN1', 'IN2', 'OUT1'], 'Common')
        self.n = n

    @property
    def parameter(self):
        function = f"""function outputs = select(signals, error)

                    num = size(signals, 1);
                    selected = zeros({self.n}, size(signals, 2));

                    counter = 0;
                    for i = 1:num
                        if error(i) ~= 0 && counter < {self.n}
                            counter = counter + 1;
                            selected(counter, :) = signals(i, :);
                        end

                        if counter >= {self.n}
                            break;
                        end
                    end

                    outputs = selected; """
        parameters = {
            'Function': function
        }
        return parameters

class SignalAlter(Logic):
    def __init__(self, ID:int=0):
        super().__init__('SignalAlter', ID, 'simulink/User-Defined Functions/MATLAB Function', ['IN1', 'OUT1'], 'Common')
        self.alter = """function y = alter(u)
                        y = u + 1;
                        end
                        """
    @property
    def parameter(self):
        parameters = {
            'Function': self.alter
        }
        return parameters

#Workspace

class ToWorkspace(Workspace):
    def __init__(self, ID:int=0, variable_name='simout', sample_time:int=-1):
        super().__init__('ToWorkspace', ID, 'simulink/Sinks/To Workspace', ['IN1'], 'Common')
        self.variable_name = variable_name
        self.sample_time = sample_time
        self.save_format = 'Structure with Time'

    @property
    def parameter(self):
        parameters = {
            'SampleTime': self.sample_time,
            'VariableName': self.variable_name,
            'SaveFormat': self.save_format
        }
        return parameters

#Port
class Inport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Inport', ID, 'simulink/Commonly Used Blocks/In1', ['IN1'], 'Common')

class Outport(Port):
    def __init__(self, ID:int=0):
        super().__init__('Outport', ID, 'simulink/Commonly Used Blocks/Out1', ['OUT1'], 'Common')

class ConnectionPort(Port):
    def __init__(self, ID:int=0, direction='left', port_type=None):
        super().__init__('ConnectionPort', ID, 'nesl_utility/Connection Port', ['RConn 1'], 'Common')
        self.direction = direction
        self.port_type = port_type
    @property
    def parameter(self):
        parameters = {
            'Orientation': self.direction,
            'Side': self.direction
        }
        return parameters

#Utilities
class Solver(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Solver', ID, 'nesl_utility/Solver Configuration', ['RConn 1'], 'Common')

class PSSimuConv(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('PSSimuConv', ID, 'nesl_utility/PS-Simulink Converter', ['INLConn 1', 'OUT1'], 'Common')

class SimuPSConv(Utilities):
    def __init__(self, ID:int=0, filter:str='filter'):
        super().__init__('SimuPSConv', ID, 'nesl_utility/Simulink-PS Converter', ['IN1', 'OUTRConn 1'], 'Common')
        self.filter = filter

    @property
    def parameter(self):
        parameters = {
            'FilteringAndDerivatives': self.filter
        }
        return parameters

class Scope(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Scope', ID, 'simulink/Commonly Used Blocks/Scope', ['IN1'], 'Common')

class Reference(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('Reference', ID, 'ee_lib/Connectors & References/Electrical Reference', ['LConn 1'], 'Both')

class Mux(Utilities):
    def __init__(self, ID:int=0, num_input:int=2):
        super().__init__('Mux', ID, 'simulink/Commonly Used Blocks/Mux', [], 'Common')
        self.num_input = num_input
        for i in range(self.num_input):
            self.port.append('IN' + str(i+1))
        self.port.append('OUT1')

    def set_input(self, num_input):
        self.num_input = num_input
        self.port.clear()
        for i in range(self.num_input):
            self.port.append('IN' + str(i + 1))
        self.port.append('OUT1')

    @property
    def parameter(self):
        parameters = {
            'Inputs': self.num_input
        }
        return parameters

class VectorConcatenate(Utilities):
    def __init__(self, ID:int=0, num_input:int=2):
        super().__init__('VectorConcatenate', ID, 'simulink/Commonly Used Blocks/Vector Concatenate', [], 'Common')
        self.num_input = num_input
        for i in range(self.num_input):
            self.port.append('IN' + str(i+1))
        self.port.append('OUT1')

    def set_input(self, num_input):
        self.num_input = num_input
        self.port.clear()
        for i in range(self.num_input):
            self.port.append('IN' + str(i + 1))
        self.port.append('OUT1')

    @property
    def parameter(self):
        parameters = {
            'NumInputs': self.num_input
        }
        return parameters


class Demux(Utilities):
    def __init__(self, ID:int=0, num_output:int=2):
        super().__init__('Demux', ID, 'simulink/Commonly Used Blocks/Demux', ['IN1'], 'Common')
        self.num_output = num_output
        for i in range(self.num_output):
            self.port.append('OUT' + str(i+1))

    def set_output(self, num_output):
        self.num_output = num_output
        self.port.clear()
        self.port.append('IN1')
        for i in range(self.num_output):
            self.port.append('OUT' + str(i + 1))

    @property
    def parameter(self):
        parameters = {
            'Outputs': self.num_output
        }
        return parameters

class CommonSwitch(Utilities):
    def __init__(self, ID:int=0, threshold:float=0):
        super().__init__('CommonSwitch', ID, 'simulink/Commonly Used Blocks/Switch', ['IN1', 'IN2', 'IN3', 'OUT1'], 'Common')
        self.threshold = threshold

    @property
    def parameter(self):
        parameters = {
            'Threshold': self.threshold
        }
        return parameters

class UnitDelay(Utilities):
    def __init__(self, ID:int=0):
        super().__init__('UnitDelay', ID, 'simulink/Discrete/Unit Delay', ['IN1', 'OUT1'], 'Common')


#Signal
class FromWorkspace(Workspace):
    def __init__(self, ID:int=0, variable_name='simin', sample_time:int=0):
        super().__init__('FromWorkspace', ID, 'simulink/Sources/From Workspace', ['OUT1'], 'Common')
        self.variable_name = variable_name
        self.sample_time = sample_time

    @property
    def parameter(self):
        parameters = {
        'SampleTime': self.sample_time,
        'VariableName': self.variable_name
        }
        return parameters

class Constant(Signal):
    def __init__(self, ID:int=0, value=1):
        super().__init__('Constant', ID, 'simulink/Sources/Constant', ['OUT1'], 'Common')
        self.value = float(value)

    @property
    def parameter(self):
        parameters = {
            'Value': self.value
        }
        return parameters



class Step(Signal):
    def __init__(self, ID:int=0, step_time:float=1, initial_value:float=0, final_value:float=1, sample_time:float=0):
        super().__init__('Step', ID, 'simulink/Sources/Step', ['OUT1'], 'Common')
        self.step_time = float(step_time)
        self.initial_value = float(initial_value)
        self.final_value = float(final_value)
        self.sample_time = float(sample_time)

    @property
    def parameter(self):
        parameters = {
            'Time': self.step_time,
            'Before': self.initial_value,
            'After': self.final_value,
            'SampleTime': self.sample_time
        }
        return parameters

class Sine(Signal):
    def __init__(self, ID:int=0, amplitude:float=1, bias:float=0, frequency:float=1, phase:float=0, sample_time:float=0):
        super().__init__('Sine', ID, 'simulink/Sources/Sine Wave', ['OUT1'], 'Common')
        self.amplitude = float(amplitude)
        self.bias = float(bias)
        self.frequency = float(frequency)
        self.phase = float(phase)
        self.sample_time = float(sample_time)

    @property
    def parameter(self):
        parameters = {
            'Amplitude': self.amplitude,
            'Bias': self.bias,
            'Frequency': self.frequency,
            'Phase': self.phase,
            'SampleTime': self.sample_time
        }
        return parameters

#Actuator
@gin.configurable()
class ElectricalActuator(Actuator):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CircuitBreaker(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5, breaker_behavior:int=2):
        super().__init__('CircuitBreaker', ID, 'ee_lib/Switches & Breakers/Circuit Breaker', ['signalINLConn 1', 'LConn 2', 'RConn 1'], 'AC')
        self.threshold = float(threshold)
        self.breaker_behavior = int(breaker_behavior)

    @property
    def parameter(self):
        parameters = {
            'threshold': self.threshold,
            'breaker_behavior': self.breaker_behavior
        }
        return parameters

@gin.configurable()
class SPSTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5):
        super().__init__('SPSTSwitch', ID, 'ee_lib/Switches & Breakers/SPST Switch', ['signalINLConn 1','LConn 2','RConn 1'], 'Both')
        self.threshold = float(threshold)

    @property
    def parameter(self):
        parameters = {
            'Threshold': self.threshold
        }
        return parameters
@gin.configurable()
class SPDTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, threshold:float=0.5):
        super().__init__('SPDTSwitch', ID, 'ee_lib/Switches & Breakers/SPDT Switch', ['signalINLConn 1','LConn 2','RConn 1','RConn 2'], 'Both')
        self.threshold = float(threshold)

    @property
    def parameter(self):
        parameters = {
            'Threshold': self.threshold
        }
        return parameters

@gin.configurable()
class SPMTSwitch(ElectricalActuator):
    def __init__(self, ID:int=0, number:int=3):
        super().__init__('SPMTSwitch', ID, 'ee_lib/Switches & Breakers/SPMT Switch', ['signalINLConn 1','LConn 2'], 'Both')
        if number < 3:
            self.number = 3
        elif number > 8:
            self.number = 8
        else:
            self.number = number
        for i in range(self.number):
            self.port.append('RConn' + ' ' + str(i+1))

    @property
    def parameter(self):
        parameters = {
            'number_throws': self.number
        }
        return parameters

    def change_throw_number(self, number):
        self.number = number
        self.port = ['signalLConn 1', 'LConn 2']
        for i in range(self.number):
            self.port.append('RConn' + ' ' + str(i+1))

#Sensor
@gin.configurable()
class ElectricalSensor(Sensor):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class CurrentSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('CurrentSensor', ID, 'ee_lib/Sensors & Transducers/Current Sensor', ['scopeOUTRConn 1', '+LConn 1', '-RConn 2'], 'Both')


@gin.configurable()
class VoltageSensor(ElectricalSensor):
    def __init__(self, ID:int=0):
        super().__init__('VoltageSensor', ID, 'ee_lib/Sensors & Transducers/Voltage Sensor', ['scopeOUTRConn 1','+LConn 1','-RConn 2'], 'Both')

#Source
@gin.configurable()
class ElectricalSource(Source):
    def __init__(self, name, ID, directory, port, current_type, source_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type
        self.source_type = source_type

@gin.configurable()
class Battery(ElectricalSource):
    def __init__(self, ID:int=0, vnom:float=12, innerR:float=2, capacity:float=50, v_1:float=11.5, ah_1:float=25, infinite=None):
        super().__init__('Battery', ID, 'ee_lib/Sources/Battery', ['+LConn 1','-RConn 1'], 'DC', 'battery')
        self.vnom = float(vnom)
        self.innerR = float(innerR)
        self.capacity = float(capacity)
        self.v_1 = float(v_1)
        self.ah_1 = float(ah_1)
        self.infinite = infinite

    @property
    def parameter(self):
        if self.infinite:
            parameters = {
                'Vnom': self.vnom,
                'R1': self.innerR
            }
        else:
            if self.v_1 > self.vnom:
                self.v_1 = self.vnom - 0.5
            if self.ah_1 / self.v_1 > self.capacity / self.vnom:
                self.ah_1 = self.v_1 * (self.capacity / self.vnom)
            parameters = {
                'prm_AH': '2',
                'Vnom': self.vnom,
                'R1': self.innerR,
                'AH': self.capacity,
                'V1': self.v_1,
                'AH1': self.ah_1
            }
        return parameters

@gin.configurable()
class VoltageSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50, dc_voltage:float=0):
        super().__init__('VoltageSourceAC', ID, 'ee_lib/Sources/Voltage Source', ['+LConn 1','-RConn 1'], 'AC', 'voltage')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)
        self.dc_voltage = float(dc_voltage)

    @property
    def parameter(self):
        parameters = {
            'dc_voltage': self.dc_voltage,
            'ac_voltage': self.peak,
            'ac_shift': self.phase_shift,
            'ac_frequency': self.frequency
        }
        return parameters


@gin.configurable()
class CurrentSourceAC(ElectricalSource):
    def __init__(self, ID:int=0, peak:float=10, phase_shift:float=10, frequency:float=50, dc_current:float=0):
        super().__init__('CurrentSourceAC', ID, 'ee_lib/Sources/Current Source', ['+LConn 1','-RConn 1'], 'AC', 'current')
        self.peak = float(peak)
        self.phase_shift = float(phase_shift)
        self.frequency = float(frequency)
        self.dc_current = float(dc_current)

    @property
    def parameter(self):
        parameters = {
            'dc_current': self.dc_current,
            'ac_current': self.peak,
            'ac_shift': self.phase_shift,
            'ac_frequency': self.frequency
        }
        return parameters

@gin.configurable()
class VoltageSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, voltage:float=10):
        super().__init__('VoltageSourceDC', ID, 'ee_lib/Sources/Voltage Source', ['+LConn 1','-RConn 1'], 'DC', 'voltage')
        self.voltage = float(voltage)

    @property
    def parameter(self):
        parameters = {
            'dc_voltage': self.voltage
        }
        return parameters

@gin.configurable()
class ControlledVoltageSource(ElectricalSource):
    def __init__(self, ID:int=0):
        super().__init__('ControlledVoltageSourceDC', ID, 'fl_lib/Electrical/Electrical Sources/Controlled Voltage Source',
                         ['signalINRConn 1','+LConn 1','-RConn 2'], 'Both', 'voltage')


@gin.configurable()
class CurrentSourceDC(ElectricalSource):
    def __init__(self, ID:int=0, current:float=10):
        super().__init__('CurrentSourceDC', ID, 'ee_lib/Sources/Current Source', ['+LConn 1','-RConn 1'], 'DC', 'current')
        self.current = float(current)

    @property
    def parameter(self):
        parameters = {
            'dc_current': self.current
        }
        return parameters


@gin.configurable()
class ControlledCurrentSource(ElectricalSource):
    def __init__(self, ID:int=0):
        super().__init__('ControlledCurrentSourceDC', ID, 'fl_lib/Electrical/Electrical Sources/Controlled Current Source',
                         ['signalINRConn 1','+LConn 1','-RConn 2'], 'Both', 'current')

#Element
@gin.configurable()
class ElectricalElement(Element):
    def __init__(self, name, ID, directory, port, current_type):
        super().__init__(name, ID, directory, port, 'Electrical')
        self.current_type = current_type

@gin.configurable()
class Capacitor(ElectricalElement):
    def __init__(self, ID:int=0, capacitance:float=10):
        super().__init__('Capacitor', ID, 'ee_lib/Passive/Capacitor', ['LConn 1','RConn 1'], 'AC')
        self.capacitance = float(capacitance)

    @property
    def parameter(self):
        parameters = {
            'c': self.capacitance
        }
        return parameters

@gin.configurable()
class VariableCapacitor(ElectricalElement):
    def __init__(self, ID:int=0, Cmin:float=1e-9):
        super().__init__('VariableCapacitor', ID, 'ee_lib/Passive/Variable Capacitor', ['signalINLConn 1','LConn 2','RConn 1'], 'AC')
        self.Cmin = float(Cmin)

    @property
    def parameter(self):
        parameters = {
            'Cmin': self.Cmin
        }
        return parameters

@gin.configurable()
class Inductor(ElectricalElement):
    def __init__(self, ID:int=0, inductance:float=10):
        super().__init__('Inductor', ID, 'ee_lib/Passive/Inductor', ['LConn 1','RConn 1'], 'AC')
        self.inductance = float(inductance)

    @property
    def parameter(self):
        parameters = {
            'L': self.inductance
        }
        return parameters

@gin.configurable()
class VariableInductor(ElectricalElement):
    def __init__(self, ID:int=0, Lmin:float=1e-6):
        super().__init__('VariableInductor', ID, 'ee_lib/Passive/Variable Inductor', ['signalINLConn 1','LConn 2','RConn 1'], 'AC')
        self.Lmin = float(Lmin)

    @property
    def parameter(self):
        parameters = {
            'Lmin': self.Lmin
        }
        return parameters


@gin.configurable()
class Resistor(ElectricalElement):
    def __init__(self, ID:int=0, resistance:float=10):
        super().__init__('Resistor', ID, 'ee_lib/Passive/Resistor', ['LConn 1', 'RConn 1'], 'Both')
        self.resistance = float(resistance)

    @property
    def parameter(self):
        parameters = {
            'R': self.resistance
        }
        return parameters

@gin.configurable()
class Varistor(ElectricalElement):
    def __init__(self, ID:int=0, vclamp:float=0.1, roff:float=10, ron:float=1, vln:float=0.1, vnu:float=100, rLeak:float=10,
                 alphaNormal:float=45, rUpturn:float=0.1, prm=None):
        super().__init__('Varistor', ID, 'ee_lib/Passive/Varistor', ['LConn 1', 'RConn 1'], 'Both')
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

    @property
    def parameter(self):
        if self.prm == 'linear':
            parameters = {
                'prm': '1',
                'vclamp': self.vclamp,
                'roff': self.roff,
                'ron': self.ron
            }
        elif self.prm == 'power-law':
            if self.vln > self.vnu:
                self.vln = self.vnu - 50
            parameters = {
                'prm': '2',
                'vln': self.vln,
                'vnu': self.vnu,
                'alphaNormal': self.alphaNormal,
                'rUpturn': self.rUpturn,
                'rLeak': self.rLeak
            }
        return parameters

@gin.configurable()
class Diode(ElectricalElement):
    def __init__(self, ID:int=0, forwardV:float=0.5, onR:float=0.01, breakV:float=500):
        super().__init__('Diode', ID, 'ee_lib/Semiconductors & Converters/Diode', ['LConn 1', 'RConn 1'], 'AC')
        self.forwardV = float(forwardV)
        self.onR = float(onR)
        self.breakV = float(breakV)

    @property
    def parameter(self):
        parameters = {
            'Vf': self.forwardV,
            'Ron': self.onR,
            'BV': self.breakV
        }
        return parameters
#mission
@gin.configurable()
class IncandescentLamp(Mission):
    def __init__(self, ID:int=0, r_0:float=0.15, r_1:float=1, Vrated:float=12, alpha:float=0.004):
        super().__init__('IncandescentLamp', ID, 'ee_lib/Passive/Incandescent Lamp', ['+LConn 1', '-RConn 1'], 'Electrical')
        self.current_type = 'Both'
        self.r_0 = float(r_0)
        self.r_1 = float(r_1)
        self.Vrated = float(Vrated)
        self.alpha = float(alpha)

    @property
    def parameter(self):
        parameters = {
            'R0': self.r_0,
            'R1': self.r_1,
            'Vrated': self.Vrated,
            'alpha': self.alpha
        }
        return parameters

@gin.configurable()
class UniversalMotor(Mission):
    def __init__(self, ID:int=0, w_rated:float=6500, P_rated:float=75, V_dc:float=200, P_in:float=160, Ltot:float=0.525):
        super().__init__('UniversalMotor', ID, 'ee_lib/Electromechanical/Brushed Motors/Universal Motor', ['+LConn 1', '-RConn 1', 'LConn 2', 'RConn 2'], 'Electrical')
        self.current_type = 'Both'
        self.w_rated = float(w_rated)
        self.P_rated = float(P_rated)
        self.V_dc = float(V_dc)
        self.P_in = float(P_in)
        self.Ltot = float(Ltot)

    @property
    def parameter(self):
        if self.P_in <= self.P_rated:
            self.P_in = self.P_rated + 50
        parameters = {
            'w_rated': self.w_rated,
            'P_rated': self.P_rated,
            'V_dc': self.V_dc,
            'P_in': self.P_in,
            'Ltot': self.Ltot
        }
        return parameters
@gin.configurable()
class Inertia(Mission):
    def __init__(self, ID:int=0, inertia:float=0.5, num_ports=2):
        super().__init__('Inertia', ID, 'fl_lib/Mechanical/Rotational Elements/Inertia', ['LConn 1', 'RConn 1'], 'Electrical')
        self.current_type = 'Both'
        self.inertia = float(inertia)
        self.num_ports = str(num_ports)
    @property
    def parameter(self):
        parameters = {
            'inertia': self.inertia,
            'num_ports': self.num_ports
        }
        return parameters
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