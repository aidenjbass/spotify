import numpy

camelot_wheel = numpy.array([
    ['0', 'A', 'B'],
    ['1', 'A-Flat Minor', 'B Major'],
    ['2', 'E-Flat Minor', 'F-Sharp Major'],
    ['3', 'B-Flat Minor', 'D-Flat Major'],
    ['4', 'F Minor', 'A-Flat Major'],
    ['5', 'C Minor', 'E-Flat Major'],
    ['6', 'G Minor', 'B-Flat Major'],
    ['7', 'D Minor', 'F Major'],
    ['8', 'A Minor', 'C Major'],
    ['9', 'E Minor', 'G Major'],
    ['10', 'B Minor', 'D Major'],
    ['11', 'F-Sharp Minor', 'A Major'],
    ['12', 'D-Flat Minor', 'E Major']
])

x = 0
y = None
i = None

while not 1 < x < 12:
    x = int(input('Enter a number 1 - 12: '))

i = str(input('Enter A or B: '))
if i == 'A' or i == 'a':
    y = 1
elif i == 'B' or i == 'b':
    y = 2
else:
    pass

print(camelot_wheel[x, y])
