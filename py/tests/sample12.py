def solve(values):
    mas = values.split(";")
    n = mas[0]
    far = mas[1:int(n)+1]
    m = mas[int(n)+1]
    sar= mas[int(n)+2:]
    x = []
    # type your code with try-except-else-finally here
    for i in far:
        b = []
        if ":" in i:
            b = i.split(" : ")
            if b[0] in sar and b[1] in sar:
                if sar.index(b[0]) > sar.index(b[1]):
                    x.append(b[0])
    y = []
    for i in sar:
        if i in x:
            y.append(i)
        
    return ",".join(y)
 
