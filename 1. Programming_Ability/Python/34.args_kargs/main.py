# *args (tuples)          non-keyword
# **kargs (dictionary)    keyword

# *args (tuples)
def print_Name(*args):
    return type(args)
print(print_Name())

def add(*nums):
    return nums
print(add(10, 2, 4))

# int for args
def create_Total(*args):
    total = 0
    for arg in args:
        total += arg
    return total
print(create_Total(10, 2, 20, 5))

# str for args
def create_Name(*args):
    for arg in args:
        print(arg, end=" ")
create_Name("Spongebob", "Squarepants")
print()
create_Name("Dr.", "Spongebob", "Squarepants")
print()
create_Name("Dr.", "Spongebob", "Harold", "Squarepants")
print()


# **kargs (dictionary)
def address_values(**kargs):
    for value in kargs.values():
        print(value)

def address_keys(**kargs):
    for key in kargs.keys():
        print(key)
        
def address_items(**kargs):
    for key, value in kargs.items():
        print(f"{key:8}: {value}")

address_values(city="Taipei", apt="&100", strict="nishi", road="guonchog", number="20")
print()
address_keys(city="Taipei", apt="&100", strict="nishi", road="guonchog", number="20")
print()
address_items(city="Taipei", apt="&100", strict="nishi", road="guonchog", number="20")
print()