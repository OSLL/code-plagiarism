def my_issub(class1, class2, gen):
    for i in gen:
        if " : " in i:
            C=i.split(" : ")
            if C[0] == class1 and C[1] == class2:
                return True
    return False

def solve(values):
    L = values.split(';')
    gen=L[1:(int(L[0])+1)]
    exp = L[(int(L[0])+2):]
    rez = []
    for i in range(1, len(exp)):
        for j in range(i-1,0,-1):
            if my_issub(exp[i],exp[j], gen):
                rez.append(exp[i])
                break
    processed_values = ','.join(rez)
    return processed_values
