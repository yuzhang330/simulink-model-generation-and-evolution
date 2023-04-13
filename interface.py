import matlab
import matlab.engine

class SimulinkInterface:
    def input_systemparameters(self):
        pass

    def input_connections(self):
        pass

    def input_subsystem(self, eng, model_name, subsystem):
        pass

    def input_components(self):
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

    def input_subsystem(self, eng, model_name, subsystem):
        # Add a subsystem to the Simulink model
        subsystem_path = f'{model_name}/{subsystem.name}_{subsystem.ID}_{subsystem.subsystem_type}'
        eng.add_block('simulink/Ports & Subsystems/Subsystem', subsystem_path, nargout=0)
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
                param_value_str = str(param_value) if not isinstance(param_value, str) else param_value
                eng.set_param(f'{subsystem_path}/{component.name}_{component.ID}', param_name, param_value_str,
                              nargout=0)

    def input_systemparameters(self):
        pass

    def input_connections(self):
        pass

    def input_components(self):
        pass