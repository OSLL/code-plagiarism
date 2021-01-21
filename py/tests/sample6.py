def solve(values):
    a=values.split(';')
    n=int(a[0])
    m=int(a[n+1])
    t1=a[1:n+1]
    t2=a[m+2:]
    dictus={}
    processed_values=[]
    for i in t1:
        b=i.split(' : ')
        if len(b) > 1:
            dictus[b[0]]=b[1]
        else:
            dictus[b[0]]=None
    err=[]
    for i in t2:
        d=dictus.get(i)
        if d in t2 and d in err:
            processed_values.append(i)
        err.append(i)
    processed_values=','.join(processed_values)
    return processed_values
