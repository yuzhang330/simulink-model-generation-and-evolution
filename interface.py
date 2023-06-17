import matlab
import matlab.engine
class SimulinkInterface:
    def input_systemparameters(self):
        pass

    def input_connections(self, eng, connection, path, type):
        pass

    def input_subsystem(self, eng, model_name, subsystem, position):
        pass

    def input_components(self, eng, model_name, component, position):
        pass

class SystemSimulinkAdapter(SimulinkInterface):
    def __init__(self, system):
        self.system = system

    def make_positions(self, input_list):
        sub_lists = []
        start_index = 0
        odd_count = 1
        while start_index < len(input_list):
            end_index = start_index + odd_count
            sub_list = input_list[start_index:end_index]
            sub_lists.append(sub_list)
            start_index = end_index
            odd_count += 2
        new_input_list = []
        for index, sublist in enumerate(sub_lists):
            for subindex, position in enumerate(sublist):
                new_position = [element + 100 * index for element in position]
                if subindex % 2 == 0:
                    new_position[0] = new_position[0] - (subindex // 2) * 100
                    new_position[2] = new_position[0] + 30
                else:
                    new_position[1] = new_position[1] - ((subindex + 1) // 2) * 100
                    new_position[3] = new_position[1] + 30
                new_input_list.append(new_position)
        return new_input_list

    def process_string(self, input_string):
        input_string = input_string.replace('id', '')
        parts = input_string.split('port')
        part_1 = parts[0].rsplit('_', 1)[0]
        part_2 = parts[1]
        return part_1, part_2

    def port_sort(self, item):
        if 'OUT' in item:
            return 0
        elif 'IN' in item:
            return 2
        else:
            return 1

    def input_components(self, eng, model_name, component, position):
        eng.add_block(component.directory, f'{model_name}/{component.name}_{component.ID}', nargout=0)
        position_matlab = matlab.double(position)
        eng.set_param(f'{model_name}/{component.name}_{component.ID}', 'Position', position_matlab, nargout=0)
        for param_name, param_value in component.parameter.items():
            param_value_str = str(param_value) if not isinstance(param_value, str) else param_value
            eng.set_param(f'{model_name}/{component.name}_{component.ID}', param_name, param_value_str,
                          nargout=0)

    def input_connections(self, eng, connection, path, type):
        if type == 'block':
            block_1, port_1 = self.process_string(connection[0])
            block_2, port_2 = self.process_string(connection[1])
            ports = [f'{block_1}/{port_1}', f'{block_2}/{port_2}']
            ports.sort(key=self.port_sort)
            modified_ports = [s.replace('IN', '').replace('OUT', '') for s in ports]
            eng.add_line(path, modified_ports[0], modified_ports[1], 'autorouting', 'on', nargout=0)
        if type == 'subsystem':
            block_1, port_1 = self.process_string(connection[0])
            if 'subsystem' in block_1:
                handle = eng.get_param(f'{path}/{block_1}/{port_1}', 'PortHandles')
                handle = handle['RConn'] - 1
            else:
                handle = eng.get_param(f'{path}/{block_1}', 'PortHandles')
                s = port_1.split(' ')
                if isinstance(handle[s[0]], float):
                    handle = handle[s[0]]
                else:
                    handle = handle[s[0]][0][int(s[1])-1]
            block_2, port_2 = self.process_string(connection[1])
            if 'subsystem' in block_2:
                handle_1 = eng.get_param(f'{path}/{block_2}/{port_2}', 'PortHandles')
                handle_1 = handle_1['RConn'] - 1
            else:
                handle_1 = eng.get_param(f'{path}/{block_2}', 'PortHandles')
                s = port_2.split(' ')
                if isinstance(handle_1[s[0]], float):
                    handle_1 = handle_1[s[0]]
                else:
                    handle_1 = handle_1[s[0]][0][int(s[1])-1]
            # handle = eng.get_param(f'{path}/{block_1}/{port_1}', 'Handle')
            # handle_1 = eng.get_param(f'{path}/{block_2}/{port_2}', 'Handle')
            eng.add_line(path, handle, handle_1, 'autorouting', 'on', nargout=0)

    def input_subsystem(self, eng, model_name, subsystem, position):
        # Add a subsystem to the Simulink model
        subsystem_path = f'{model_name}/{subsystem.name}_{subsystem.subsystem_type}_{subsystem.ID}'
        eng.add_block('simulink/Ports & Subsystems/Subsystem', subsystem_path, nargout=0)
        position_matlab = matlab.double(position)
        eng.set_param(f'{subsystem_path}', 'Position', position_matlab, nargout=0)
        eng.delete_line(subsystem_path, 'In1/1', 'Out1/1', nargout=0)
        eng.delete_block(f'{subsystem_path}/In1', nargout=0)
        eng.delete_block(f'{subsystem_path}/Out1', nargout=0)
        positions = [[100, 100, 130, 130]] * len(subsystem.component_list)
        positions = self.make_positions(positions)
        for index, component in enumerate(subsystem.component_list):
            eng.add_block(component.directory, f'{subsystem_path}/{component.name}_{component.ID}', nargout=0)
            position_matlab = matlab.double(positions[index])
            eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', 'Position', position_matlab, nargout=0)
            for param_name, param_value in component.parameter.items():
                if param_name == 'Function':
                    fcn_name = eng.get_param(f'{subsystem_path}/{component.name}_{component.ID}', 'MATLABFunctionConfiguration')
                    eng.setfield(fcn_name, 'FunctionScript', param_value, nargout=0)
                else:
                    param_value_str = str(param_value) if not isinstance(param_value, str) else param_value
                    eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', param_name, param_value_str,
                                  nargout=0)
            if component.name == 'FromWorkspace':
                component.variable_name = f"simin_{component.ID}_{subsystem.subsystem_type}_{subsystem.ID}"
                time_values = matlab.double([0])
                data_values = matlab.double([[1]])
                my_signal = {
                    'time': time_values,
                    'signals': {
                        'values': data_values
                    }
                }
                eng.workspace[component.variable_name] = eng.struct(my_signal)
                eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', 'VariableName', component.variable_name,
                              nargout=0)
        for connection in subsystem.connections:
            self.input_connections(eng, connection, subsystem_path, 'block')

    def input_system_parameters(self, eng, model_name):
        eng.set_param(model_name, 'Solver', self.system.solver, nargout=0)
        eng.set_param(model_name, 'StopTime', str(self.system.stop_time), nargout=0)

    def input_system(self, eng, model_name):
        self.input_system_parameters(eng, model_name)
        positions = [[100, 100, 130, 130]] * (len(self.system.subsystem_list) + len(self.system.component_list))
        positions = self.make_positions(positions)
        for index, subsys in enumerate(self.system.subsystem_list):
            self.input_subsystem(eng, model_name, subsys, positions[index])
            i = index + 1
        for index, component in enumerate(self.system.component_list):
            self.input_components(eng, model_name, component, positions[index+i])
        for connection in self.system.connections:
            self.input_connections(eng, connection, model_name, 'subsystem')

    def change_parameter(self, eng, model_name, parameter_name, parameter_value, component_name, component_id,
                                      subsystem_type=None, subsystem_id=None):
        param_value_str = str(parameter_value) if not isinstance(parameter_value, str) else parameter_value
        if subsystem_type and subsystem_id is not None:
            eng.set_param(f'{model_name}/subsystem_{subsystem_type}_{subsystem_id}/{component_name}_{component_id}',
                          parameter_name, param_value_str, nargout=0)
        else:
            eng.set_param(f'{model_name}/{component_name}_{component_id}', parameter_name, param_value_str, nargout=0)

class Implementer:
    def input_to_simulink(self, system, eng, simulink_model_name):
        interf = SystemSimulinkAdapter(system)
        model_name = simulink_model_name
        eng.new_system(model_name, nargout=0)
        eng.open_system(model_name, nargout=0)
        interf.input_system(eng, model_name)

    def change_parameter(self, model_name, parameter_name, parameter_value, component_name, component_id,
                         subsystem_type=None, subsystem_id=None):
        eng = matlab.engine.start_matlab()
        param_value_str = str(parameter_value) if not isinstance(parameter_value, str) else parameter_value
        if subsystem_type and subsystem_id is not None:
            eng.set_param(f'{model_name}/subsystem_{subsystem_type}_{subsystem_id}/{component_name}_{component_id}',
                          parameter_name, param_value_str, nargout=0)
        else:
            eng.set_param(f'{model_name}/{component_name}_{component_id}', parameter_name, param_value_str, nargout=0)








