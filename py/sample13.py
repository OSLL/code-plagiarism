def solve(values):
    values=list(map(lambda x: list(x.split(" : ")), values.split(';')))
    pv=[]
    b=int(values[0][0])+1
    for i in range(b+1,len(values)):
        k=1
        while(k<b and values[i][0]!=values[k][0]):
            k+=1
        if(k<b and len(values[k])>1):
            s=values[k][1]
            e=b+1
            while(e<i and values[e][0]!=s):
                e+=1
            if (e<i):
                pv.append(values[i][0])     
    return ','.join(pv)
