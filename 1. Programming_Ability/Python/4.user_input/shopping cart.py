item = input("What would u like to buy?: ")
price = int(input("Pls enter the price: "))
quantity = int(input("Pls enter the quantity of the item: "))
total = price * quantity

print(f"You've bought {quantity} x {item}/s.")
print(f"Your total is ${total}.")