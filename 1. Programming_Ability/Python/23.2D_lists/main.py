# 2D 

# fruits = ["Apple", "Banana", "Pineapple"]
# Cars   = ["Ferari", "Honda", "Tesla"]
# Verbs  = ["Raining", "Crying", "Screaming"]

# summarise = [fruits, Cars, Verbs]

# # print(summarise[0][1])

# for collection in summarise:
#     for words in collection:
#         print(words, end=" ")
#     print()


nums = ([1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        ["*", 0, "#"])

for collection in nums:
    for num in collection:
        print(num, end=" ")
    print()