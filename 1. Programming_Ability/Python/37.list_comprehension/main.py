# List comprehension = A concise way to create lists in Python
#                       Compact and easier to read than traditional loops
#                       [expression for value in iterable if condition]

double = []
for x in range(1, 11):
    double.append(x * 2)
print(double)

doubles = [x * 2 for x in range(1, 11)]
print(doubles)

triples = [y * 3 for y in range(1, 11)]
print(triples)

squares = [z**z for z in range(1, 11)]
print(squares)

fruits = ["apple", "banana", "pineapple", "coconut"]
fruits = [fruit.capitalize() for fruit in fruits]
# fruits = [fruit.capitalize() for fruit in ["apple", "banana", "pineapple", "coconut"]] 
print(fruits)

fruit_chars = [fruit[0] for fruit in fruits]
print(fruit_chars)