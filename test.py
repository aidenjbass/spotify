import re

flag = False
text = input("Enter some text: ")

while not flag:
    if re.search('[*+-]', text):
        print("contains invalid characters")
        flag = True
    else:
        print('valid')
        break
