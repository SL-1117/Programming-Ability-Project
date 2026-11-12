# compound interest calculator

principle = 0
rate = 0
time = 0

while True:
    principle = float(input("Pls enter a correct amount: "))
    if principle <= 0:
        print("Principle can't be less or equal to zero.")
    else:
        break

while True:
    rate = float(input("Pls enter a correct amount: "))
    if rate <= 0:
        print("Principle can't be less or equal to zero.")
    else:
        break

while True:
    time = int(input("Pls enter a correct amount: "))
    if time <= 0:
        print("Principle can't be less or equal to zero.")
    else:
        break

final = principle * pow((1 + rate / 100), time)

print(f"The new Balance is ${round(final)} after {time} years")