def solve(values):
    values = values.split(';')
    
    number1 = int(values[0])
    values1 = values[1:1 + number1]
    
    number2 = int(values[1 + number1])
    values2 = values[2 + number1:]

    d = dict()
    passed = []
    not_passed = []
    
    for x in values1:
        x = x.split(" : ")
        if x[0] not in d.keys():
            if len(x) == 1:
                d[x[0]] = "None"
            else:
                d[x[0]] = x[1]
                if x[1] not in d.keys():
                    d[x[1]] = "None"

    for x in values2:
        flag = 0
        t = x
        if t == '':
            continue
        while d[t] != "None":
            if d[t] in passed:
                flag = 1
                break
            else:
                t = d[t]
                
        if t in passed:
            flag = 1
            
        if flag:
            not_passed.append(x)
        else:
            passed.append(x)
                
    return ",".join(not_passed)
