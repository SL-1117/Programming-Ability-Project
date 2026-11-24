# return = statement used to end a function
#          and send a result back to the caller

def hello(greeting, first, last, name):
    print(f"{greeting}, {first} {last} {name}")

# first one is positional arg, others are keyword
hello("Hello", first="Wick", last = "John", name="III")
hello("Hello", last="John", name="III", first="Wick")

# end is a keyword arg found in built in print
for num in range(1, 11):
    print(num, end=" ")
print()

# You got some keyword elements to use in print
print("1", "2", "3", "4", "5", sep="-")

def getphone(country, area, first, last):
    print(f"{country}-{area}-{first}-{last}")

getphone(country=1, area=123, first=456, last=7890)
getphone(1, area=123, first=456, last=7890)
getphone(area=123, first=456, last=7890, country=1)