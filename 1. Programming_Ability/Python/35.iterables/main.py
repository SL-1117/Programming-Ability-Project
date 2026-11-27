# Iterables

# tuples
# dictionary
# sets
# lists

my_tuple = (1, 2, 3, 4, 5)
my_list = [1, 2, 3, 4, 5]
my_set = {1, 2, 3, 4, 5}

dictionary = {"A": "A",
              "B": "B",
              "C": "C"}

for num in my_tuple:
    print(num, end="")
print()

for num in my_list:
    print(num, end="")
print()

for num in my_set:
    print(num, end="")
print()

for key, value in dictionary.items():
    print(f"{key}: {value}")