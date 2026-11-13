# Set   = {} unordered and immutable, but Add/Remove OK. NO dulicates


Cars = {"Ferari", "Honda", "Tesla", "Toyota", "Audi"}

# print(len(Cars))
# print(help(Cars))
# print(dir(Cars))
print("Lambogini" in Cars)

# We cannot use the index because set is unordered
# print(Cars[0])

Cars.add("Audi")
# Cars.remove("Tesla")
# Cars.pop()
# Cars.clear()

print(Cars)