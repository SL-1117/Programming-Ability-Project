# function

# happy birthday song

# def Player(name):
#     print(f"Happy birthday to {name}")
#     print("You are old")
#     print("Happy birthday to you")

#     return 0

# name = "Shiro_Leaf"
# Player("Shiro_Leaf")
# print(Player("Shiro_Leaf"))


# # arithmetic calculation

# def plus(x, y):
#     return x + y

# def substract(x, y):
#     return x - y

# def multiply(x, y):
#     return x * y

# def divide(x, y):
#     return x / y

# x = 20
# y = 4

# print(plus(x, y))
# print(substract(x, y))
# print(multiply(x, y))
# print(divide(x, y))

def create_name(first, last):
    first = first.capitalize()
    last = last.capitalize()
    return first + " " + last

full_name = create_name("SpongeBob", "squaRepants")

print(full_name)