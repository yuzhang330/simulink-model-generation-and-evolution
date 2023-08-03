# simulink-model-generation-and-evolution

This software enables Simulink model Generation and Evolution for RL in the electrical domain.
This software has three modules that follow object-oriented programming principles in Python: Generator module, Interface module, and Upgrader module.

Generator module is designed for automatically generating pseudo-random Python models.

Interface module is designed for implementing the Python model in Simulink.

Upgrader module is designed for evolving the generated Python model with fault-tolerant design patterns.


## Installation
This software needs to install packages gin==0.1.6
and matlab engine==9.13.7

## Usage
Model generation process:

* Initialize ModelDirector class with DC/ACModelBuilder class instance and an optional gin-config file.
- Call 'build_model' function of ModelDirector with an optional random seed to start generation process.
  
Model implementation process:
- Initialize Implementer class with SystemSimulinkAdapter class instance.
- Call 'input_to_simulink' function of Implementer with generated Python model and model name in Simulink to start implementation process.
  
Model Evolution process:
- Initialize BasicUpgrader class with generated Python model and SingleUpgrader/CombineUpgrader class for upgrading with different fault-tolerant design patterns.
- Call 'upgrade' function of SingleUpgrader/CombineUpgrader with designated sensor subsystem and one of fault tolerance/pattern name to start evolution process.
- Implement the Python model again in Simulink with 'input_to_simulink' function

Corresponding codes located in main.py file

