#!/usr/bin/env python
import sys
import re
import os
import copy


# DL sources:
# ...
# cd libname
# mkdir build
# cd build
# make VERBOSE=1 > ../../build.txt

# ./cmakeToLutin.py build.txt bzip2



build_output_file = sys.argv[1]
global_lib_name = sys.argv[2]

def create_directory_of_file(file):
	path = os.path.dirname(file)
	try:
		os.stat(path)
	except:
		os.makedirs(path)

def file_write_data(path, data):
	#create_directory_of_file(path)
	file = open(path, "w")
	file.write(data)
	file.close()
	return True

list_of_library_generated = []

def genrate_version(version):
	file_write_data("version.txt", version);

list_of_flags_default = {
    "c":[],
    "c++":[],
    "S":[],
    "link":[],
   }

depend_transcript = {}

def genrate_lutin_file(lib_name, list_of_files, list_of_flags, list_of_dependency, comilator_version, list_include_path, binary=False):
	if binary == False:
		pass
	basic_name = copy.deepcopy(lib_name)
	tmp_base = "lib" + global_lib_name + "_"
	if     len(lib_name) > len(tmp_base)\
	   and lib_name[:len(tmp_base)] == tmp_base:
		lib_name = lib_name[len(tmp_base):]
	list_of_library_generated.append(lib_name.replace("_","-"))
	test_unit = False
	sample = False
	tools = False
	##print("check lib name : '" + lib_name + "'")
	if lib_name.find("test") != -1:
		##print("    ==> test")
		test_unit = True
	if lib_name.find("sample") != -1:
		##print("    ==> sample")
		sample = True
	if lib_name.find("tool") != -1:
		##print("    ==> tools")
		tools = True
	for elem in list_of_files:
		if elem.find("test") != -1:
			##print("    ==> test 2")
			test_unit = True
		elif elem.find("sample") != -1:
			##print("    ==> sample 2")
			sample = True
	lib_name = lib_name.replace(global_lib_name, "")
	if test_unit == True:
		lib_name = lib_name.replace("tests", "")
		lib_name = lib_name.replace("test", "")
		if lib_name == "":
			lib_name = global_lib_name + "-test"
		else:
			lib_name = global_lib_name + "-test-" + lib_name
	elif sample == True:
		lib_name = lib_name.replace("samples", "")
		lib_name = lib_name.replace("sample", "")
		if lib_name == "":
			lib_name = global_lib_name + "-sample"
		else:
			lib_name = global_lib_name + "-sample-" + lib_name
	elif tools == True:
		lib_name = lib_name.replace("tools", "")
		lib_name = lib_name.replace("tool", "")
		if lib_name == "":
			lib_name = global_lib_name + "-tools"
		else:
			lib_name = global_lib_name + "-tools-" + lib_name
	else:
		lib_name = global_lib_name + "-" + lib_name
	##print("                     new name: '" + lib_name + "'")
	depend_transcript[basic_name] = lib_name
	# remove all unneeded element flags:
	#-I
	list_of_include = copy.deepcopy(list_of_flags_default)
	# -D
	list_of_define = copy.deepcopy(list_of_flags_default)
	# other
	list_of_other = copy.deepcopy(list_of_flags_default)
	#print("list of flags: ")
	for type in ["c", "c++", "S", "link"]:
		for elem in list_of_flags[type]:
			if elem in ["-m64", "-o3", "-o2", "-o1", "-o0", "-O3", "-O2", "-O1", "-O0", "-fPIC"]:
				continue
			if elem == "-pthread":
				if "pthread" not in tmp_dependency_list:
					list_of_dependency.append("pthread")
				continue
			if elem in ["-fabi-version=0", '-I"/usr/include"']:
				# just remove it ..
				continue
			if elem[:2] == "-D":
				#print("DEFINE: " + elem)
				list_of_define[type].append(elem)
				continue
			if elem[:2] == "-I":
				if    elem == '-I"."' \
				   or elem == '-I.':
					continue
				if elem[:9] in '-I"bin.v2':
					continue
				if elem[:4] in '-I"/':
					if "/usr/include/python3.6" == elem[3:-1]:
						if elem[3:-1]+"m" not in list_of_include[type]:
							list_of_include[type].append(elem[3:-1]+"m")
						# TODO: depend on python lib
					else:
						if elem[3:-1] not in list_of_include[type]:
							list_of_include[type].append(elem[3:-1])
					continue
				# TODO : Do it better :
				
				print("INCLUDE: " + elem )
				if os.path.isdir(global_lib_name + "/" + global_lib_name + "/" +elem[3:-1]):
					if global_lib_name + "/" + global_lib_name + "/" +elem[3:-1] not in list_of_include[type]:
						list_of_include[type].append(global_lib_name + "/" + global_lib_name + "/" +elem[3:-1])
				else:
					if global_lib_name + "/" +elem[3:-1] not in list_of_include[type]:
						list_of_include[type].append(global_lib_name + "/" +elem[3:-1])
				continue
			if elem[:2] in '-l':
				if elem[2:] not in list_of_dependency:
					list_of_dependency.append(elem[2:])
				continue
			#print("???: " + elem)
			if elem not in list_of_other[type]:
				list_of_other[type].append(elem)
	
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	if binary == False:
		out += "	return \"LIBRARY\"\n"
	else:
		out += "	return \"BINARY\"\n"
		out += "\n"
		if test_unit == True:
			out += "def get_sub_type():\n"
			out += "	return 'TEST'\n"
		elif sample == True:
			out += "def get_sub_type():\n"
			out += "	return 'SAMPLE'\n"
	out += "\n"
	out += "def get_desc():\n"
	#out += "	return \"" + global_lib_name + ":" + lib_name.replace("_","-") + " library\"\n"
	out += "	return \"" + lib_name.replace("_","-") + " library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "#def get_maintainer():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	list_dir = []
	if len(list_of_files) != 0:
		out += "	my_module.add_src_file([\n"
		for item in list_of_files:
			if os.path.dirname(item) not in list_dir:
				list_dir.append(os.path.dirname(item))
			#out += "	    '" + global_lib_name + "/" + item +"',\n"
			out += "	    '" + item +"',\n"
		out += "	    ])\n"
		out += "	\n"
	
	if len(list_dir) != 0:
		out += "	my_module.add_header_file([\n"
		for elem in list_dir:
			out += "	    '" + elem + "/*.hpp',\n"
			out += "	    '" + elem + "/*.hxx',\n"
			out += "	    '" + elem + "/*.h',\n"
			out += "	    '" + elem + "/*.H',\n"
		#out += "	    recursive=True,\n"
		#out += "	    destination_path='" + global_lib_name + "')\n"
		out += "	    ], clip_path='" + global_lib_name + "')\n"
		out += "	\n"
	
	if    test_unit == True \
	   or sample == True \
	   or True:
		if    len(list_dir) != 0 \
		   or len(list_include_path) != 0:
			out += "	my_module.add_path([\n"
			for item in list_dir:
				out += "	    '" + item +"',\n"
			for item in list_include_path:
				out += "	    '" + item +"',\n"
			out += "	    ], export=False)\n"
			out += "	\n"
	
	out += "	\n"
	
	for type in ["c", "c++", "S", "link"]:
		if len(list_of_define[type]) != 0:
			if type == "cpp":
				out += "	my_module.add_flag('c++', [\n"
			elif type == "S":
				out += "	my_module.add_flag('s', [\n"
			else:
				out += "	my_module.add_flag('" + type + "', [\n"
			for item in list_of_define[type]:
				out += "	    '" + item +"',\n"
			out += "	    ])\n"
			out += "	\n"
	out += "	\n"
	for type in ["c", "c++", "S"]: # NO LINK
		if len(list_of_other[type]) != 0:
			out += "	my_module.add_flag('" + type + "', [\n"
			for item in list_of_other[type]:
				out += "	    '" + item +"',\n"
			out += "	    ])\n"
			out += "	\n"
	out += "	\n"
	for type in ["c", "c++", "S", "link"]:
		if len(list_of_include[type]) != 0:
			out += "	my_module.add_path([\n"
			for item in list_of_include[type]:
				out += "	    '" + item +"',\n"
			if type == "cpp":
				out += "	    ], type='c++')\n"
			elif type == "S":
				out += "	    ], type='s')\n"
			else:
				out += "	    ], type='" + type + "')\n"
			out += "	\n"
	
	for type in ["c", "c++", "S"]:
		if comilator_version[type] != []:
			year = 1990
			gnu = "False"
			## print("check : " + comilator_version[type])
			if comilator_version[type] in ["c90"]:
				year = 1990
				gnu = "False"
			elif comilator_version[type] in ["c89"]:
				year = 1989
				gnu = "False"
			elif comilator_version[type] in ["c99", "c9x"]:
				year = 1999
				gnu = "False"
			elif comilator_version[type] in ["c++98"]:
				year = 1998
				gnu = "False"
			elif comilator_version[type] in ["c++03"]:
				year = 2003
				gnu = "False"
			elif comilator_version[type] in ["c11", "c1x", "c++11", "c++0x"]:
				year = 2011
				gnu = "False"
			elif comilator_version[type] in ["c++14", "c++1y"]:
				year = 2014
				gnu = "False"
			elif comilator_version[type] in ["c++17", "c++1z"]:
				year = 2017
				gnu = "False"
			elif comilator_version[type] in ["gnu90"]:
				year = 1990
				gnu = "True"
			elif comilator_version[type] in ["gnu89"]:
				year = 1989
				gnu = "True"
			elif comilator_version[type] in ["gnu++98"]:
				year = 1998
				gnu = "True"
			elif comilator_version[type] in ["gnu99", "gnu9x"]:
				year = 1999
				gnu = "True"
			elif comilator_version[type] in ["gnu++03"]:
				year = 2003
				gnu = "True"
			elif comilator_version[type] in ["gnu11", "gnu1x", "gnu++11", "gnu++0x"]:
				year = 2011
				gnu = "True"
			elif comilator_version[type] in ["gnu++14", "gnu++1y"]:
				year = 2014
				gnu = "True"
			elif comilator_version[type] in ["gnu++17", "gnu++1z"]:
				year = 2017
				gnu = "True"
			out += "	my_module.compile_version('" + type + "', " + str(year) + ", gnu=" + gnu + ")\n"
			
	out += "	my_module.add_depend([\n"
	#out += "	    'z',\n"
	#out += "	    'm',\n"
	out += "	    'cxx',\n"
	#out += "	    '" + global_lib_name + "-include',\n"
	for item in list_of_dependency:
		if item in depend_transcript:
			out += "	    '" + depend_transcript[item] +"',\n"
		else:
			out += "	    '" + item +"',\n"
	out += "	    ])\n"
	out += "	return True\n"
	out += "\n"
	out += "\n"
	
	file_write_data("lutin_" + lib_name.replace("_","-") + ".py", out);


def generate_global_include_module():
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	out += "	return \"LIBRARY\"\n"
	out += "\n"
	out += "def get_desc():\n"
	out += "	return \"" + global_lib_name + " include library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "#def get_maintainer():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	out += "	my_module.compile_version('c++', 2011)\n"
	out += "	my_module.add_header_file(\n"
	out += "	    '" + global_lib_name + "/" + global_lib_name + "/*',\n"
	out += "	    recursive=True,\n"
	out += "	    destination_path='" + global_lib_name + "')\n"
	out += "	return True\n"
	out += "\n"
	out += "\n"
	
	file_write_data("lutin_" + global_lib_name + "-include.py", out);
	

def generate_global_module(list_of_module):
	out = ""
	out += "#!/usr/bin/python\n"
	out += "import lutin.debug as debug\n"
	out += "import lutin.tools as tools\n"
	out += "import os\n"
	out += "\n"
	out += "def get_type():\n"
	out += "	return \"LIBRARY\"\n"
	out += "\n"
	out += "def get_desc():\n"
	out += "	return \"" + global_lib_name + " include library\"\n"
	out += "\n"
	out += "#def get_licence():\n"
	out += "#	return \"UNKNOW\"\n"
	out += "\n"
	out += "def get_compagny_type():\n"
	out += "	return \"org\"\n"
	out += "\n"
	out += "def get_compagny_name():\n"
	out += "	return \"" + global_lib_name + "\"\n"
	out += "\n"
	out += "def get_version():\n"
	out += "	return \"version.txt\"\n"
	out += "\n"
	out += "def configure(target, my_module):\n"
	out += "	my_module.compile_version('c++', 2011)\n"
	out += "	my_module.add_depend([\n"
	out += "	    '" + global_lib_name + "-include',\n"
	for item in list_of_module:
		out += "	    '" + item +"',\n"
	out += "	    ])\n"
	out += "\n"
	out += "\n"
	file_write_data("lutin_" + global_lib_name + ".py", out);

def clean_path(path_list):
	out = []
	need_break = False
	while need_break == False:
		need_break = True
		for iii in range(0,len(path_list)):
			elem = path_list[iii];
			if iii == len(path_list)-1:
				elem_next = ""
			else:
				elem_next = path_list[iii+1];
			if elem_next == "..":
				need_break = False
				for jjj in range(iii+2,len(path_list)):
					out.append(path_list[jjj]);
				path_list = out
				out = []
				break;
			elif elem == ".":
				pass
			else:
				out.append(path_list[iii]);
	return out

def reformat_path(path):
	list_elem = []
	for elem in path.split("/"):
		list_elem.append(elem.replace("/", ""));
	tmp_elem = clean_path(list_elem);
	out = ""
	if path[0] == "/":
		out = "/"
	for elem in tmp_elem:
		out += elem + "/"
	return out


with open(build_output_file) as commit:
	lines = commit.readlines()
	if len(lines) == 0:
		print("Empty build ....")
		sys.exit(1)
	list_of_file = []
	list_of_flags = copy.deepcopy(list_of_flags_default)
	std_selected = copy.deepcopy(list_of_flags_default)
	current_path = os.getcwd()
	list_include_path = []
	# first line
	for line in lines:
		#print("line : " + line[-6:-2])
		"""
		if     len(line) > 6 \
		   and line[-6:-2] == ".cpp":
			print("element : " + line)
		"""
		## print("-----------------------------------------------------------------------------")
		m = re.search('^.*Entering directory \'(.*)\'$', line)
		if m != None:
			if len(m.groups()) == 1:
				current_path = m.groups()[0]
				if     len(current_path) >= len(os.getcwd()) \
				   and current_path[:len(os.getcwd())] == os.getcwd():
					current_path = current_path[len(os.getcwd())+1:]
				#print("change directory: '" + current_path + "'")
			continue
		
		m = re.search('^(/usr/bin/|pkgdata: )?(cc|gcc|g\+\+|clang\+\+|clang)(.*)$',line) #(([a-zA-Z0-9_\-]*)\.(cpp|c|cxx|S|s))$', line)
		if m != None:
			if len(m.groups()) != 3:
				print("  reject: " + line);
				continue
			#print("CMD : " + line[:-1])
			list_elem = m.groups()[2].split(" ");
			
			tmp_binary_name = None
			tmp_library_shared_name = None
			tmp_library_static_name = None
			tmp_compile_file = None
			tmp_type = ""
			tmp_flag_list = []
			tmp_dependency_list = []
			tmp_list_of_flags = []
			remove_next = False
			tmp_std_selected = copy.deepcopy(list_of_flags_default)
			tmp_tmp_std_selected = ""
			##print ("                    " + list_elem[-1])
			for elem_id in range(0, len(list_elem)):
				elem = list_elem[elem_id]
				if remove_next == True:
					remove_next = False
					continue
				if elem == "-o":
					remove_next = True;
					# find output ==> parse it
					elem_out = list_elem[elem_id+1]
					"""
					m = re.search('^(.*\.(cpp|c|cxx|S|s))$', list_elem)
					if     m != None \
					   and len(m.groups()) == 2:
						print("compile element: " + os.path.join(current_path, list_elem))
						continue
					"""
					m = re.search('^(.*\.o)$', elem_out)
					if m != None:
						#print("compile element:   " + os.path.join(current_path, elem_out))
						continue
					
					m = re.search('^(.*\.a)$', elem_out)
					if m != None:
						tmp_library_static_name = elem_out.split("lib")[-1].split(".a")[0]
						print("link element(a):   " + tmp_library_static_name)
						continue
					
					m = re.search('^(.*\.so(\.[0-9]+)*)$', elem_out)
					#m = re.search('^.*/(lib.*\.so)(\.[0-9]+)*$', elem_out)
					if m != None:
						tmp_library_shared_name = elem_out.split("lib")[-1].split(".so")[0]
						## print("link element(so):  " + tmp_library_shared_name)
						#for elem in m.groups():
						#	print("     " + str(elem))
						#print("compile element: " + os.path.join(current_path, list_elem))
						#print("compile element: " + os.path.join(current_path, list_elem))
						continue
					
					tmp_binary_name = elem_out.split("bin/")[-1];
					## print("link binary:       " + tmp_binary_name)# + "     : " + elem_out)
				#print( elem)
				if     len(elem) >= 3 \
				   and (    elem[-3:] == "cpp" \
				         or elem[-3:] == ".cc" \
				         or elem[-2:] == ".C" \
				         or elem[-2:] == ".c" \
				         or elem[-2:] == ".s" \
				         or elem[-2:] == ".S"):
					
					if elem[-3:] == "cpp":
						tmp_type = "c++"
					elif elem[-2:] == "cc":
						tmp_type = "c++"
					elif elem[-2:] == ".C":
						tmp_type = "c++"
					elif elem[-2:] == ".c":
						tmp_type = "c"
					elif elem[-2:] == ".S":
						tmp_type = "S"
						# print("oooooooooooooooooooooooooooooooooo: " + elem)
					elif elem[-2:] == ".s":
						tmp_type = "S"
					tmp_compile_file = os.path.join(current_path, elem)
					## print("                 source:   " + tmp_compile_file)
					continue
				if elem[:2] == "-l":
					if elem == "-ldl":
						continue
					#print("              depend: " + elem[2:])
					if elem[2:] not in tmp_dependency_list:
						tmp_dependency_list.append(elem[2:])
					continue
				if elem in ["", \
				            "-o0", "-o1", "-o2", "-o3", "-o4", "-o5", \
				            "-O0", "-O1", "-O2", "-O3", "-O4", "-O5", \
				            "-x", "c", "-W", "-o", "-c", "assembler-with-cpp",\
				            "-D_REENTRANT"]:
					continue
				if     len(elem) > 5 \
				   and elem[:5] == "-std=":
					tmp_tmp_std_selected = elem[5:]
					#print("STD type: " + std_selected)
					continue
				if     len(elem) > 2 \
				   and (    elem[-2:] == ".o"
				         or elem[-2:] == ".a"):
					#print(" remove : " + elem)
					continue;
				if     len(elem) > 2 \
				   and elem[:2] == "-I":
					include_path = reformat_path(os.path.join(current_path, elem[2:]))
					#print("requesst inclide of " + current_path + " ==> " + os.path.join(current_path, elem[2:]))
					#print("requesst inclide of " + current_path + " ==> " + reformat_path(os.path.join(current_path, elem[2:])))
					if include_path not in list_include_path:
						list_include_path.append(include_path)
					continue
				if     len(elem) > 2 \
				   and elem[:2] == "-L":
					continue
				if elem in ["-shared", "-DPIC", "fPIC"]:
					continue
				if     len(elem) >= 4 \
				   and elem[:4] == "-Wl,":
					continue
				if elem not in list_of_flags:
					#print("      " + flag)
					tmp_list_of_flags.append(elem)
			##print("  ZZZZZZZ: " + line);
			if tmp_type == "":
				tmp_type = "link"
			if len(tmp_list_of_flags) != 0:
				## print("              flags:")
				for flag in tmp_list_of_flags:
					if flag in list_of_flags[tmp_type]:
						## print("                    " + flag)
						pass
					else:
						if flag.find('"') != -1:
							###print("                  * " + flag)
							if     len(flag) >= 1 \
							   and flag[0] == '"':
								flag = flag[1:]
							if     len(flag) >= 2 \
							   and not flag[-2:] == '\\"' \
							   and flag[-1] == '"':
								flag = flag[:-1]
							flag = flag.replace('\\"', '\\\\"')
							flag = '"' + flag + '"'
							###print("                 => " + flag)
						if len(flag) != 0:
							list_of_flags[tmp_type].append(flag);
						## print("                  * " + flag)
			if tmp_tmp_std_selected != "":
				## print("              STD type: " + tmp_tmp_std_selected)
				std_selected[tmp_type] = tmp_tmp_std_selected;
			
			######################################
			## update in the bigger list
			######################################
			
			#print("   CCCCCCCCCC    '" + str(tmp_binary_name) + "' '" + str(tmp_library_shared_name) + "' '" + str(tmp_library_static_name) + "'")
			if    tmp_binary_name != None \
			   or tmp_library_shared_name != None \
			   or tmp_library_static_name != None:
				# create new elemeent
				if tmp_binary_name != None:
					genrate_lutin_file(tmp_binary_name, list_of_file, list_of_flags, tmp_dependency_list, std_selected, list_include_path, binary=True)
				elif tmp_library_shared_name != None:
					genrate_lutin_file(tmp_library_shared_name, list_of_file, list_of_flags, tmp_dependency_list, std_selected, list_include_path)
				else:
					genrate_lutin_file(tmp_library_static_name, list_of_file, list_of_flags, tmp_dependency_list, std_selected, list_include_path)
				## print("   CCCCCCCCCC clean   ")
				list_of_file = []
				list_include_path = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				std_selected = copy.deepcopy(list_of_flags_default)
				continue
			if tmp_compile_file != None:
				list_of_file.append(tmp_compile_file)
				pass
			
			
			continue
		continue
		
		m = re.search('^/usr/bin/ar(.*)lib(.*)\.a(.*)$', line)
		if m != None:
			
			print("element : " + str(len(m.groups())))
			for elem in m.groups():
				print("     " + elem)
			if len(m.groups()) == 3:
				genrate_lutin_file(m.groups()[1], list_of_file, list_of_flags)
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
			
		
		
		"""
		
		m = re.search('^(.*)/usr/bin/ar"(.*)"((.*)/([a-zA-Z0-9_\-.]*)\.a)"(.*)$', line)
		if m != None:
			## we do not use AR element ==> in boost just a double compilation ...
			if len(m.groups()) == 6:
				#print("element : " + line)
				## print("  to: " + m.groups()[4] + " (.a)")
				# Remove it only keep the .so
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
		# ln -f -s 'libboost_wave.so.1.66.0' 'stage/lib/libboost_wave.so'
		"""
		
		"""
		#m = re.search('(.*/([a-zA-Z0-9_\-\.]*?)\.so)', line)
		m = re.search('^(.*)"(g\+\+|gcc|clang)"(.*)$', line)
		if m != None:
			#print("element : " + str(len(m.groups())))
			for elem in m.groups():
				#print("     " + elem)
				list_elem = elem.split('" "')
				list_elem[-1] = list_elem[-1].split('"')[0]
				for val in list_elem:
					if val[-2:] == ".o":
						continue
					lib_name = val.split('/')[-1].split(".so")[0]
					if lib_name[:3] == "lib":
						lib_name = lib_name[3:].replace("_","-")
						#print("         " + lib_name)
						list_of_flags["cpp"].append('-l' + lib_name)
		"""
		"""
		m = re.search('^(.*)\'((.*)/([a-zA-Z0-9_\-.]*)\.so)\'$', line)
		if m != None:
			 " ""
			print("element : " + str(len(m.groups())))
			for elem in m.groups():
				print("     " + elem)
			"" "
			if len(m.groups()) == 4:
				#print("element : " + line)
				#print("  to: " + m.groups()[3] + " (.so)")
				#if "libboost_container" == m.groups()[3]:
				#	exit(0)
				genrate_lutin_file(m.groups()[3], list_of_file, list_of_flags)
				##for item in list_of_file:
				##	print("          " + item)
				list_of_file = []
				list_of_flags = copy.deepcopy(list_of_flags_default)
				continue
		"""
		

"""
#create version file
genrate_version("1.66.0")
# generate a global inclue
generate_global_include_module()
# generate a global library
generate_global_module(list_of_library_generated)
"""

"""
/home/heero/dev/perso/framework/generic-library/icu-lutin/icu/source/data
./out/Linux_x86_64/debug/staging/clang/icu-pkg/icu-pkg.app/bin/icu-pkg -d ./out/build/icudt60l --list -x \* ./in/icudt60l.dat -o out/tmp/icudata.lst

./out/Linux_x86_64/debug/staging/clang/icu-pkgdata/icu-pkgdata.app/bin/icu-pkgdata -O ../data/icupkg.inc -q -c -s /home/heero/dev/perso/framework/generic-library/icu-lutin/icu/source/data/out/build/icudt60l -d ../lib -e icudt60  -T ./out/tmp -p icudt60l -m dll -r 60.2 -L icudata ./out/tmp/icudata.lst
"""