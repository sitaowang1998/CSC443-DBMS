import matplotlib.pyplot as plt

f = open('sort_result', 'r')

p512B = []
p512P = []
p1024B = []
p1024P = []
p2048B = []
p2048P = []


while True:
    line1 = f.readline()
    if line1 == '':
        break
    line2 = f.readline()
    pSize = int(line1.split(' ')[1])
    B = int(line1.strip('\n').split(' ')[4])
    page = int(line2.split(' ')[5])

    if pSize == 512:
        p512B.append(B)
        p512P.append(page)
    elif pSize == 1024:
        p1024B.append(B)
        p1024P.append(page)
    elif pSize == 2048:
        p2048B.append(B)
        p2048P.append(page)
    else:
        print(pSize)
        raise ValueError

f.close()

fig, ax = plt.subplots()
ax.plot(p512B, p512P, 'r', label='512')
ax.plot(p1024B, p1024P, 'g', label='1024')
ax.plot(p2048B, p2048P, 'b', label='2048')
ax.semilogx()
ax.legend(loc='upper center')
plt.savefig('sort_result.png')