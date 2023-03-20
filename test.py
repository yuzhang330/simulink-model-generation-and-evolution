import gin
from system import *
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
list_one = [('a', 'n'), ('a', 'b'), ('c', 'd')]
list_two = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']

unused_letters = [letter for letter in list_two if letter not in [pair[0] for pair in list_one] and letter not in
                  [pair[1] for pair in list_one]]

print(unused_letters)
#%%
import random

list2 = ["a", "b", "c", "d", "e"]
list1 = [1, 2, 3]
def make_pairs(list1, list2):
    if len(list1) > len(list2):
        raise ValueError("List 1 cannot be longer than List 2")

    list1_copy = list1.copy()
    pairs = []
    for item2 in list2:
        if len(list1_copy) == 0:
            list1_copy = list1.copy()
        item1 = random.choice(list1_copy)
        pairs.append((item1, item2))
        list1_copy.remove(item1)

    return pairs
print(make_pairs(list1, list2))
#%%
def separate_strings(input_list):
    plus_list = []
    minus_list = []
    for string in input_list:
        if '+' in string:
            plus_list.append(string.replace('+', ''))
        if '-' in string:
            string = string.replace('-', '')
            minus_list.append(string)
    return plus_list, minus_list
a,b = separate_strings(['+/aaa','+/bbb','-/ccc','/ddd'])
#%%
r1 = Resistor()
r2 = Resistor()
# sys = Subsystem()
# sys.add_component(r1,r2)
# sys.list_components()
print(r1.take_port(['LConn','RConn']))
#%%
str = ['thresholdL','thrL','L']
for s in str:
    if 'L' in s and 'threshold' not in s:
        print(s)

