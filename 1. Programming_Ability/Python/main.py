# damn, I even started learning python at the same week that I have to prepare for midterm.

# Strings
first_messages = "Hello, what u up to?"
first_email = "liwei20051117@gmail.com"
phone_number = "0929753777"

# Integers
Age = 21
Height = 1.71
Weight = 65

# Float 
price = 10.99999

# Boolean
is_stupid = True
for_sale = False
is_online = True

print(first_messages)
print(f"This is a message {first_messages}")
print(f"This is a message {first_messages.upper()}")

print(f"Your age is {Age} and you height is {Height} and your weight is {Weight}")

print(f"The price of the banana is ${price:.5f}")

print(f"Are u a stupid?")
if is_stupid:
    print(f"{is_stupid}")

else:
    print(f"{is_stupid}")

print(f"Is this for sale?")
if for_sale:
    print(f"Yes, u can buy it!")

else: 
    print(f"No, this is not for sale!")