import gin
from components import *
#%%

gin.parse_config_file('my_config.gin')

cb = CircuitBreaker()
type(cb.threshold)
# cv = SPDTSwitch()
# cb.randomize_attributes()
#%%

cb.list_attributes()
#%%
import random
group_sizes = []
num_components = 5
while num_components > 0:
    rand_num = random.randint(1, num_components)
    group_sizes.append(rand_num)
    num_components -= rand_num
components = [10,20,30,40,50]
groups = []
for size in group_sizes:
    group = []
    for i in range(size):
        component = random.choice(components)
        group.append(component)
        components.remove(component)
    groups.append(group)
#%%
len(groups)