# while {}

# name = (input("Pls enter ur name: "))

# while name == "" or len(name) > 5:
#     print("You didn't enter ur name or the name is longer than 5 digits.")
#     name = (input("Pls enter ur name."))
# print(f"Hey, {name}")

food = input("Pls enter the food u like (enter q to exit): ")

while not food == "q":
    print(f"You like {food}.")
    food = input("Pls enter the food u like (enter q to exit): ")

print("Bye bye.")
