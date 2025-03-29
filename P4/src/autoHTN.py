import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	# if item == 'wood':
	# 	if state.made_wooden_axe[ID] is True: 
	# 		return [('produce_wood', ID)]
	# 	else:
	# 		return [('produce', ID, 'wooden_axe')]

	if ("should_make_" + item) in state.__dict__:
		if (getattr(state, "should_make_"+ item)[ID] is False):
			return False

	if ("made_" + item) in state.__dict__:
		if (getattr(state, "made_"+ item)[ID] is True):
			return False
		else:
			setattr(state, "made_"+ item, {ID: True})


	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	# print("In Make Method")
	produces, requires, consumes, time = rule
	def method (state, ID):
		ret = []

		# return [('have_enough', ID, 'bench', 1), ('have_enough', ID, 'stick', 2), ('have_enough', ID, 'plank', 3), ('op_craft_wooden_axe_at_bench', ID)]
		if requires:
			for tool, quantityforTool in requires.items():
				ret.append(('have_enough', ID, tool, quantityforTool))
		
		if consumes:
			if 'ingot' in consumes:
				for item, quantity in consumes.items():
						ret.append(('have_enough', ID, item, quantity))
			else:	
				for item, quantity in reversed(list(consumes.items())):
						ret.append(('have_enough', ID, item, quantity))
			# for item, quantity in consumes.items():
			# 	# print("What need", item, "How Many:", quantity)
			# 	ret.append(('have_enough', ID, item, quantity))
		
		operator_name = "op_" + name.replace(" ", "_")
		ret.append((operator_name, ID))

		# print("Produces name:", produces.key)
		# method.__name__ = 'produce_{}'.format(produces.key)
		# print("What we are returning: ", ret)
		return ret
	# based on ChatGPT for renaming a nested function
	# item, amount = produces.items()
	# print("Produces name:", item)
	item_name = next(iter(produces))
	method.__name__ = name.replace(" ", "_")
	return method

def declare_methods (data):
	# print("In declare Method")
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	

	name = ""
	produces = ""
	requires = ""
	consumes = ""
	time = 0
	method_dict = {}

	for d in data["Recipes"]:
		# print("Recipe:", d)

		name = d
		produces = data["Recipes"][d]['Produces']
		# print("Produces:", data["Recipes"][d]['Produces'])
		if 'Requires' in data["Recipes"][d]:
			requires = data["Recipes"][d]['Requires']
		else:
			requires = ""
			# print("Requires:", data["Recipes"][d]['Requires'])
		if 'Consumes' in data["Recipes"][d]:
			consumes = data["Recipes"][d]['Consumes']
		else:
			consumes = ""
			# print("Consumes:", data["Recipes"][d]['Consumes'])
		time = data["Recipes"][d]['Time']
		# print("Time:", data["Recipes"][d]['Time'])	
		m = make_method(name, (produces, requires, consumes, time))
		name = 'produce_{}'.format(next(iter(produces)))

		# print("Name:", name, "Produces:", produces, "Requires:", requires, "Consumes:", consumes, "Time:", time)
		
		# print(f"name: {name}, m: {m}")
		if name in method_dict:
			method_dict[name].append({'method': m, 'time': time})
		else:
			method_dict[name] = [{'method': m, 'time': time}]

		# Sorting by 'time' key in each dictionary inversely
		# method_dict[name].sort(key=lambda x: x['time'], reverse=True)
		# Sorting by 'time' key in each dictionary
		method_dict[name].sort(key=lambda x: x['time'])

	
	for name, methods in method_dict.items():
		# Extract the 'method' part from each dictionary in the list
		method_functions = [method_dict['method'] for method_dict in methods]
		pyhop.declare_methods(name, *method_functions)
		# print(f"name: {name}, methods: {method_functions}")

	
	pass			

def make_operator (rule):
	# print("In Make operator")
	produces, requires, consumes, time, name = rule
	def operator (state, ID):
		# your code here

		if state.time[ID] < time:
			return False
		
		if requires:
			for tool, quantity in requires.items():
				if getattr(state, tool)[ID] < quantity:
					print("Not enough of tool: ", tool)
					return False  # Not enough of a required tool

		if consumes:
			for item, quantity in consumes.items():
				if getattr(state, item)[ID] < quantity:
					print("Not enough of item: ", item)
					return False  # Not enough of a required consumable

		state.time[ID] -= time
		if consumes:
			for item, quantity in consumes.items():
				print(f"It Be Consuming {item} in amount {quantity}")
				getattr(state, item)[ID] -= quantity


		if produces:
			for item, quantity in produces.items():
				getattr(state, item)[ID] += quantity
				
		return state
	operator_name = "op_" + name.replace(" ", "_")
	operator.__name__ = operator_name
	return operator

def declare_operators (data):
	# print("Declaring Operator")
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok
	
	# for d in data["Recipes"]:
	# 	print("Recipe:", d)
	# 	name = d

	# 	operator_name = "op_" + name.replace(" ", "_")
		
	# 	operator = make_operator(operator_name)
	# 	pyhop.declare_operators(operator)

	name = ""
	produces = ""
	requires = ""
	consumes = ""
	time = 0

	for d in data["Recipes"]:
		# print("Recipe:", d)
		name = d
		produces = data["Recipes"][d]['Produces']
		# print("Produces:", data["Recipes"][d]['Produces'])
		if 'Requires' in data["Recipes"][d]:
			requires = data["Recipes"][d]['Requires']
		else:
			requires = ""
			# print("Requires:", data["Recipes"][d]['Requires'])
		if 'Consumes' in data["Recipes"][d]:
			consumes = data["Recipes"][d]['Consumes']
		else:
			consumes = ""
			# print("Consumes:", data["Recipes"][d]['Consumes'])
		time = data["Recipes"][d]['Time']
		# print("Name:", name, "Produces:", produces, "Requires:", requires, "Consumes:", consumes, "Time:", time)
		
		# print("Time:", data["Recipes"][d]['Time'])	
		op1 = make_operator((produces, requires, consumes, time, name))
		pyhop.declare_operators(op1)

	pass

def add_heuristic (data, ID):
	# print("Calling a Heuristic")
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	
	goals = []
	for item, num in data['Goal'].items():
		goals.append({'item': item, 'num': num})

	item_goals = [goal['item'] for goal in goals]

	wood_required_from_item_goals = 0
	wood_craft_time = 0

	if "wood" in item_goals:
		wood_required_from_item_goals += goals[item_goals.index("wood")]['num']

	if "plank" in item_goals:
		wood_required_from_item_goals += goals[item_goals.index("plank")]['num'] / 4
		wood_craft_time += goals[item_goals.index("plank")]['num'] / 4
	
	if "stick" in item_goals:
		wood_required_from_item_goals += goals[item_goals.index("stick")]['num'] / 8
		wood_craft_time += ((goals[item_goals.index("stick")]['num'] / 2) + 1) / 4

	if "iron_axe" not in item_goals:
		state.should_make_iron_axe[ID] = False

	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here

		if "wood" in item_goals and state.should_make_wooden_axe[ID] is True or state.should_make_stone_axe[ID] is True:
			wood_left_needed = wood_required_from_item_goals - state.wood[ID]
			if (wood_left_needed * 4) <= state.time[ID]:
				if ("wooden_axe" not in item_goals) and ("stone_axe" not in item_goals):
					state.should_make_stone_axe[ID] = False
					state.should_make_wooden_axe[ID] = False

		if curr_task == ('produce', 'agent', 'iron_pickaxe') and ('have_enough', 'agent', 'stone_pickaxe', 1) in tasks:
			return True

		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})
		made_item = "made_" + item
		setattr(state, made_item, {ID: False})
		should_make_item = "should_make_" + item
		setattr(state, should_make_item, {ID: True})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	# state = set_up_state(data, 'agent', time=1000) # allot time here
	state = set_up_state(data, 'agent', time=100) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	#pyhop.print_operators() 
	#pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

	# pyhop.pyhop(state, [('have_enough', 'agent', 'cobble', 1)], verbose=3) # this doesnt work......

