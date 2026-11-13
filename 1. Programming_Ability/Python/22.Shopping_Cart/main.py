foods = []
prices = []
total = 0

while True:
    food = input("Pls enter the food that u would like to buy (press q to quit): ")

    if food.lower() == "q":
        break
    else:
        price = float(input("Pls enter the price of the food: "))

    foods.append(food)
    prices.append(price)

print("----- YOUR SHOPPING CART -----")

for food in foods:
    print(food, end=" ")

for price in prices:
    total += price

print()
print(f"Your total is ${total}.")