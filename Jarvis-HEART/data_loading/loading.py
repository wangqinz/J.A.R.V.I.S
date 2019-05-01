import os, sys,json,csv

base = "weather in "
keyword = "San Francisco"
inputs = base + keyword
csv_path = "./raw.csv"
training_data_path = "./test_loading.json"
####### define template split delimit ########### 
notation_mark = "%#%"
module_mark = "$$"
module_input_mark = "--$m"
module_value_mark = "--$v"
value_mark = "$"

module_single_heading = "--$sh"
module_single_value = "--$sv"

module_mtp_mark = "$$$"
module_mtp_value = None
module_mtp_value_mark = "--v$"
################## global variables########################
within_module_input = False
within_mtp_module_input = False
within_base_input = False
common_examples = []

base_input = {}
base_input["template"] = []
within_base_value = False
base_val = []
multi_val = {}
fst_row_heading = False
#################################################



def update_list(base_input,base_val,common_examples):
	intent = base_input["intent"]
	entity = base_input["entity"]
	if len(base_val) == 0:
		for tmplate in base_input["template"]:
			obj = {}
			obj['intent'] = intent
			obj['text'] = tmplate
			obj['entities'] = []
			common_examples.append(obj)
	else:
		for tmplate in base_input["template"]:
			for ele in base_val:
				obj = {}
				obj["intent"] = intent
				obj["text"] = tmplate.replace(value_mark, ele)
				valid, start, end = get_st_ed(obj["text"],ele)
				obj["entities"] = [{"value":ele,"entity":entity,"start":start,"end":end}]
				common_examples.append(obj)
	return

def handle_normal_module(row):
	global within_base_input
	global within_base_value
	global fst_row_heading
	params = row.replace("\n","").split(",")
	if row.strip() == module_input_mark and within_base_input == False:
		within_base_input = True
		fst_row_heading = True
		return
	if row.strip() == module_input_mark and within_base_input == True:
		within_base_input = False
		return	
	if row.strip() == module_value_mark and within_base_value == False:
		within_base_value = True
		return
	if row.strip() == module_value_mark and within_base_value == True:
		within_base_value = False
		return	

	if within_base_input:
		if fst_row_heading:
			base_input["intent"] = params[0]
			base_input["entity"] = params[1]
			fst_row_heading = False
		# if len(params) >1:
		else:
			base_input["template"].extend(params)
		return

	if within_base_value:
		base_val.extend(params)
		return

def handle_multi_module(row):
	global within_base_input
	global module_mtp_value
	global fst_row_heading
	params = row.replace("\n","").split(",")
	if row.strip() == module_input_mark and within_base_input == False:
		within_base_input = True
		fst_row_heading = True
		return
	if row.strip() == module_input_mark and within_base_input == True:
		within_base_input = False
		return	
	if module_mtp_value_mark in row.strip() and module_mtp_value == None:
		module_mtp_value = row.strip()[3:]
		return
	if module_mtp_value_mark in row.strip() and module_mtp_value != None:
		module_mtp_value = None
		return	

	if within_base_input:
		if fst_row_heading:
			base_input["intent"] = params[0]
			base_input["entity"] = {ele.split("|")[1]: ele.split("|")[0] for ele in params[1:]}
			fst_row_heading = False
		# if len(params) >1:
		else:
			base_input["template"].extend(params)
		return
	if module_mtp_value:
		if module_mtp_value in multi_val:
			multi_val[module_mtp_value].extend(params)
		else:
			multi_val[module_mtp_value] = params
		return


def update_from_multiple(common_examples):
	print(base_input)
	print(multi_val)
	intent = base_input['intent']
	entities = base_input['entity']
	idx_ref, prev_vals = cross_product(multi_val,entities)
	for ele in prev_vals:
		print(ele)
		for temp in base_input['template']:
			obj = {}
			obj['intent'] = intent
			for i in range(len(ele)):
				temp = temp.replace(idx_ref[i],ele[i])
			obj['text'] = temp
			obj["entities"] = []
			for i in range(len(ele)):
				entity_obj = {}
				valid, start, end = get_st_ed(temp,ele[i])
				entity_obj['value'] = ele[i].strip()
				entity_obj['entity'] = entities[idx_ref[i]].strip()
				entity_obj['start'] = start
				entity_obj['end'] = end
				obj["entities"].append(entity_obj)
			common_examples.append(obj)



def load_data_from_csv(filepath):	
	'''
	read data from csv file, form common examples section, return a list of dictionaries
	*	neglect notation and empty lines
	*	find start/end property of keywords
	'''
	# within_s_module_input = False
	# single_module_qset = {}
	global within_module_input
	global within_mtp_module_input

	with open(filepath,encoding='utf-8') as file:
		rownum = 0
		for row in file:
			rownum += 1
			if rownum %5 == 0:
				print("loading row: "+ str(rownum))
			if "%#%" in row or row.strip() == "":
				## indicating the notation line
				continue
			## define judgement for switch-off module input
			if row.strip() == module_mark and not within_module_input:
				within_module_input = True
				continue

			## end module input section, update global data structure
			if row.strip() == module_mark and within_module_input:
				update_list(base_input,base_val,common_examples)
				reset_global_variable()
				continue

			if within_module_input:
				handle_normal_module(row)
				continue
			## define if withi. multi-module input
			if row.strip() == module_mtp_mark and not within_mtp_module_input:
				within_mtp_module_input = True
				continue

			if row.strip() == module_mtp_mark and within_mtp_module_input:
				##update multi-input
				update_from_multiple(common_examples)
				reset_global_variable()
				continue

			if within_mtp_module_input:
				handle_multi_module(row)
				continue

	# print("\n",print_lod(common_examples))
	return common_examples

def write_training_json(common_examples, des):
	with open(des,"w") as file:
		file.write('''
{"rasa_nlu_data": {
	"common_examples": [
''')
		length = len(common_examples)
		for i in range(length):
			base_ele = str(common_examples[i]).replace("'",'"').replace('"re ',"'re ")
			if i != length-1:
				sentence = base_ele+",\n"
			else:
				sentence = base_ele
			file.write(sentence)

		file.write('''
	],
	"regex_features": [],
	"entity_synonyms": []
	}
}\n''')
		
		file.close()


def print_lod(examples):
	for ele in examples:
		print(ele)

def get_st_ed(input, keyword):
	st = input.find(keyword)
	if st == -1:
		return None, -1, -1
	return keyword, st, st+len(keyword)

def reset_global_variable():
	global within_module_input
	global within_mtp_module_input
	global within_base_input
	global within_base_value
	global fst_row_heading
	global base_input
	global base_val
	global multi_val
	within_module_input = False
	within_mtp_module_input = False
	within_base_input = False
	within_base_value = False
	fst_row_heading = False
	base_input = {}
	base_input["template"] = []
	base_val = []
	multi_val = {}
	return

def cross_product(multi_val,entities):
	'''
	multi_val: a dictionary storing v1 -> all possible values
	entities: a dictionary matching entity with their representations
		ex: location: v1
	return
		- list of list value results
		- a key-val pair indicating index
	'''
	idx_ref = {}
	prev_vals = []
	idx = 0
	for key,val in multi_val.items():
		prev_vals.append(val)
		idx_ref[idx] = key
		idx += 1
	##make production
	ret = [[]]
	for x in prev_vals:
		ret = [i + [y] for y in x for i in ret]
	return idx_ref,ret






if __name__ == '__main__':
	##invoke: python helper.py <function> <keyword>

	if sys.argv[1] == 'd': # d for data
		print(sys.argv)
		# keyword, st, ed =  get_st_ed(sys.argv[2], sys.argv[3])
		keyword, st, ed =  get_st_ed(inputs, keyword)
		print(keyword, st, ed)

	if sys.argv[1] == 'lfc':
		common_examples = load_data_from_csv(csv_path)
		write_training_json(common_examples, training_data_path)
	if sys.argv[1] == "w":
		write_training_json(None, training_data_path)







# # print(params)
# obj = {}
# obj["intent"] = params[0]
# obj["text"] = params[1]
# obj["entities"] = []
# if params[2] != "":
# 	keys = params[2].split("|")
# 	values = params[3].split("|")
# 	for i in range(len(keys)):
# 		child = {}
# 		child["value"] = values[i]
# 		child["entity"]= keys[i]
# 		valid, start, end = get_st_ed(params[1],values[i])
# 		child["start"] = start
# 		child["end"] = end
# 		obj["entities"].append(child)
# common_examples.append(obj)
################################################
################ helper function ################


