# time table

num1 = int(input("Pls enter ur first num: "))
num2 = int(input("Pls enter ur second num: "))

for x in range(num1, num2 + 1):
    for y in range(1, num2 + 1):
        print(f"{x}*{y} ", end="")
    print()