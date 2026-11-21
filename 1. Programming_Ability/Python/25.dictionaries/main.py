# dictionary = a collection of {key:value} pairs
#              ordered and changeable. no duplicates

capitals = {"USA": "Washington D.C.", 
            "India": "NewDelhi", 
            "China": "Beijing", 
            "Russia": "Moscow"}

# print(dir(capitals))
# print(help(capitals))

# print(capitals.get("Moscow"))
# capitals.pop("Russia")
# capitals.update({"Taiwan": "Taipei"})
# capitals.update({"Taiwan": "Beijing"})
# capitals.clear()

# capitals.update({"India": "Newdelhi"})
# capitals.popitem()

# if capitals.get("Taiwan"):
#     print("There is Taiwan.")
# else: 
#     print("There is no Taiwan.")

# for key in capitals.keys():
#     print(key)

# for value in capitals.values():
#   print(value)

# items = capitals.items()
# print(capitals.items())

for key, value in capitals.items():
    print(f"{key}: {value}")

# print(capitals)
