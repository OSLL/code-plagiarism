def check_par_child(A, B, iterable):
	for i in iterable:
		if " : " in i == True:
			splited = i.split(" : ")
			if splited[0] is A and splited[1] is B:
					return True
	return False


def solve(v):
	YES = []
	NO = []
	v = v.split(';')
	n1 = int(v[0])
	v1 = v[1:1 + n1]
	k = 2
	n2 = int(v[1 + n1])
	v2 = v[2 + n1:]
	STORAGE = dict()
	for i in v1:
		i = i.split(" : ")
		if i[0] not in STORAGE.keys():
			if len(i) == 1:
				STORAGE[i[0]] = "None"
			else:
				STORAGE[i[0]] = i[1]
				if i[1] not in STORAGE.keys():
					STORAGE[i[1]] = "None"
	for i in v2:
		flag = 0
		param = i
		if param == '':
			continue
		while STORAGE[param] != "None":
			if STORAGE[param] in YES:
				flag = 1
				break
			else:
				param = STORAGE[param]
		if param in YES:
			flag = 1
		if flag == True:
			NO.append(i)
		else:
			YES.append(i)
	return ",".join(NO)
