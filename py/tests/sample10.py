def solve(values):
    def spl():
        nonlocal values
        n = int(values[0])
        val = values[1:n+1]
        values = values[n+1:]
        return val
    
    res = list()
    values = values.split(';')
    first, second = [spl() for i in range(2)]
    d = dict()
    
    for  i in first:
        k = i.split(' : ')[::-1]
        for j in k[:]:
            try:
                k = k[1:]
                if j not in d.keys():
                    d[j] = k
                else:
                    d[j] += k
            except IndexError:
                break
                
    for i in second:
        d[i].append(1)
        for j in d.keys():
            if i in d[j] and d[j][-1] == 1:
                res.append(i)
                break
                
    res = ','.join(res)
    return res
