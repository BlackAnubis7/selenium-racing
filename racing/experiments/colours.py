bit4 = list(range(30, 38)) + list(range(90, 98))
for c in bit4:
    print(f'\033[{c}mColour {c}\033[0m')
for c in bit4:
    print(f'\033[{c+10}mBackground {c+10}\033[0m')
