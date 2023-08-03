from components import *
from system import *
from model_builder import *
from interface import *
import matlab
import matlab.engine
from upgrader import *
#%%
# initialize model generator
gin.parse_config_file('my_config.gin')
director = ModelDirector(DCBuilder())
# generate models
sys = director.build_model(seed=45)
#%%
# initialize interface
interf = Implementer(SystemSimulinkAdapter)
#%%
# implement model
interf.input_to_simulink(sys, 'my_simulink_model4')
#%%
# change model parameter
interf.change_parameter('my_simulink_model4', parameter_name='dc_current', parameter_value=15, component_name='CurrentSourceDC',
                        component_id=0, subsystem_type='source_current', subsystem_id=0)
#%%
# change control signal
my_signal = {
    'time': matlab.double([0]),
    'signals': {
        'values': matlab.double([[1]])
    }
}
interf.change_component_control_variable(sys, variable_value=my_signal, component_name='ControlledCurrentSourceDC', component_id=0,
                                  subsystem_type='source_current', subsystem_id=0)
#%%
# initialize upgrader
up = BasicUpgrader(sys)
#%%
# upgrade with single pattern
sigup = SingleUpgrader(up)
sigup.upgrade(pattern_name='voter', subsystem_type='sensor_voltage', subsystem_id=0)

#%%
# upgrade with combined pattern
comup = CombineUpgrader(up)
comup.upgrade(subsystem_type='sensor_voltage', subsystem_id=0, target=5)

#%%
# implement upgrede
interf.input_to_simulink(sys, 'my_simulink_model4')
