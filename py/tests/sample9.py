def solve(x):
    x = x.split(';')
    n = int(x[0])
    pr = []
    line = []
    i = 1
    while not x[i].isdigit():
        pr.append(x[i])
        i +=1
        
    m = int(x[i])
    for j in range(i+1, len(x)):
        line.append(x[j])
    nas = []
    par = []
    for i in range(n):
            if ' : ' not in pr[i]:
                nas.append(pr[i])
                par.append('no')
            else:
                pr[i] = pr[i].split(' : ')
                nas.append(pr[i][0])
                par.append(pr[i][1])
   # print(nas)
   # print(par)
    d = dict(zip(nas, par))
   # print(d)
    line.reverse()
    ans = []
   # print(line)
    count = 0
    for i in range(m):
        if line[i] in d and d[line[i]] != 'no' and d[line[i]] in line:
            if line.index(d[line[i]]) > i:
                ans.append(line[i])
    ans.reverse()
    ans = ','.join(ans)
    return ans
