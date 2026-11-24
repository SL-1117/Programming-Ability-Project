# default arguments

def net_price(list_price, discount=0, tax=0.05):
    return list_price * (1 - discount) * (1 + tax)

print(net_price(1000))
print(net_price(1000, 0.5))
print(net_price(1000, 0.5, 0))

import time

# def count(start=1, end=2):
#     for x in range(start, end):
#         print(x)
#         time.sleep(1)
#     print("Time's up!")

def count2(end, start=1):
    for x in range(start, end+1):
        print(x)
        time.sleep(1)
    print("Time's up!")

# count()
count2(5)