# concession stand program

menu = {"popcorn": 5.0,
        "pretzel": 3.5,
        "soda": 10.0,
        "chicken": 20.0,
        "turkey": 30.0,
        "fries": 3.0,
        "nachos": 7.99,
        "chips": 2.99}

cart = []
total = 0

print("========== MENU ==========")
for item, price in menu.items():
    print(f"{item:10}: ${price:.2f}")
print("==========================")

while True:
    food = input("Select the food you'd like to eat (type Q/q to quit): ").lower()

    if food == "q":
        print("You left.")
        break
    elif menu.get(food) is not None: 
        cart.append(food)      
        total += menu.get(food)  
    else: 
        print("That's not on the menu.")

print("You bought food down below: ")
for item in cart:
    print(f"{item}", end=" ")

print()
print(f"The total price is ${total:.2f}.")