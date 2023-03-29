import gin
from system import *
from components import *
from model_builder import *
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
print(r1.take_port(['Conn']))
print(len(r1.take_port(['Conn'])[0]))
#%%
str = ['thresholdL','thrL','L']
for s in str:
    if 'L' in s and 'threshold' not in s:
        print(s)
#%%
r = Varistor(prm='power-law')
#%%
i = [1]
p = []
if i and p:
    print(2)
elif i:
    print('i')
elif p:
    print('p')
#%%
s1 = Constant()
s2 = Step()
r = Resistor()
cv1 = SimuPSConv()
cv2 = SimuPSConv()
c1 = CircuitBreaker()
c2 = CircuitBreaker()
sys = Subsystem()
sys.add_component(s1,s2,r,c1,c2,cv1,cv2)
resistor = [r for r in sys.component_list if r.component_type == 'Element']
switchs = [switch for switch in sys.component_list if switch.component_type == 'Actuator']
signal = [signal for signal in sys.component_list if signal.component_type == 'Signal']
converter = [converter for converter in sys.component_list if converter.name == 'SimuPSConv']
index_sig = 0
index_in = 0
index_out = 0
for switch in switchs:
    for port in switch.get_port_info():
        if 'signal' in port:
            sys.add_connection((port.replace('signal', ''), converter[index_sig].get_port_info()[1])
                                     , (converter[index_sig].get_port_info()[0], signal[index_sig].get_port_info()[0]))
            index_sig += 1
        else:
            sys.add_connection((port, resistor[0].get_port_info()[1]))
#%%
play,conn = sys.list_played_components()
#%%
def find_adjacent_elements(tuples_list, elements_list):
    adjacent_elements1 = []
    for element in elements_list:
        for tup in tuples_list:
            if element in tup:
                index = tup.index(element)
                adjacent_elements1.append(tup[1 - index])
                break
    adjacent_elements = []
    for element in adjacent_elements1:
        temp = []
        for tup in tuples_list:
            if element in tup:
                index = tup.index(element)
                temp.append(tup[1 - index])
        if len(temp) >= 2:
            adjacent_elements.append(temp)

    return adjacent_elements
listA = [('a', 'b'), ('n', 'b'), ('b', 'm'), ('c', 'd'), ('o', 'c'), ('d', 'h'), ('e', 'f'), ('k', 'f'), ('y', 'u')]
listB = ['a', 'c', 'e']
l = find_adjacent_elements(listA,listB)
#%%
s = 'SimuPSConv_id1_port2'
parts = s.split('_', 2)
s1 =  '_'.join(s.split('_', 2)[:2])
played_and_signal = [('SimuPSConv_id1_port2','a'),('SimuPSConv_id1_port1','b'),('c','d')]
temp = []
for tup in played_and_signal:
    e = [element for element in tup if s1 in element]
    if e:
        index = tup.index(e[0])
        temp.append(tup[1 - index])
#%%
s = [instance for instance in sys.component_list if instance.name == 'CircuitBreaker' and instance.ID == 1]
index_list = [i for i, instance in enumerate(sys.component_list) if instance == s[0]]
#%%
def replace_elements(input_list, old_elements, new_elements):
    output_list = []
    old_elements_map = dict(zip(old_elements, new_elements))

    for pair in input_list:
        first_element = pair[0] if pair[0] not in old_elements_map else old_elements_map[pair[0]]
        second_element = pair[1] if pair[1] not in old_elements_map else old_elements_map[pair[1]]
        output_list.append((first_element, second_element))

    return output_list

input_list = [('b', 'a'), ('c', 'd'), ('e', 'f')]
old_elements = ['a', 'c']
new_elements = ['m', 'n']

result = replace_elements(input_list, old_elements, new_elements)
#%%

def find_paths(tuples_list, start, end):
    def path(visited, current):
        if current == end:
            result.append(visited)
            return

        for pair in tuples_list:
            if current in pair:
                next_node = pair[0] if pair[1] == current else pair[1]
                if pair not in visited:
                    path(visited + [pair], next_node)

    result = []
    path([], start)
    return result

tuples_list = [('a', 'b_1_1_in'), ('c', 'b_1_1_out'), ('c', 'd'), ('c','e'),('e', 'd'), ('c', 'f'), ('d', 'g'), ('h', 'i'), ('a', 'k'), ('k', 'l'), ('k', 'e')]
start_element = 'a'
end_element = 'e'
result = find_paths(tuples_list, start_element, end_element)
print(result)
#%%
def extract_elements(tuples, elements):
    result = []
    for element in elements:
        chain = [element]
        print(chain)
        for t in tuples:
            for p in chain:
                if p in t:
                    next_p = t[0] if t[1] == p else t[1]
                    chain.append(next_p)
        result.append(chain)

    return result


input_tuples = [('a', 'b'), ('c', 'b'), ('c', 'd'), ('m', 'd'), ('c', 'f'), ('h', 'i'), ('a', 'k'), ('l', 'e')]
input_elements = ['a', 'e']
output = extract_elements(input_tuples, input_elements)
print(output)
#%%
def remove_after_third_underscore(s):
    count = 0
    for i, char in enumerate(s):
        if char == '_':
            count += 1
            if count == 3:
                return s[:i]
    return s
def find_paths(tuples_list, start, end):
    def path(visited, current):
        if current == end:
            result.append(visited)
            return

        for pair in tuples_list:
            new_pair = (remove_after_third_underscore(pair[0]), remove_after_third_underscore(pair[1]))
            if current in new_pair:
                next_node = new_pair[0] if new_pair[1] == current else new_pair[1]
                if pair not in visited:
                    path(visited + [pair], next_node)

    result = []
    path([], start)
    return result
tuples_list = [('a', 'b_1_1_in'), ('c', 'b_1_1_out'), ('c', 'd'), ('c','e'),('e', 'd'), ('c', 'f'), ('d', 'g'), ('h', 'i'), ('a', 'k'), ('k', 'l'), ('k', 'e')]
start_element = 'a'
end_element = 'e'
result = find_paths(tuples_list, start_element, end_element)
print(result)