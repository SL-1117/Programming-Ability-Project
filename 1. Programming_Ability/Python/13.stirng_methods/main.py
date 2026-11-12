user_name = input("Pls enter your name (without any spaces, digits): ")

# result = len(name)
# result = name.upper()
# result = name.lower()
# result = name.capitalize()
# result = name.find("h")
# result = name.rfind("h")
# result = name.isdigit()
# result = name.isalpha()
# result = name.count(" ")
# result = name.replace("-", " ")

if user_name.isalpha() == False or user_name.find(" ") > 0:
    print("Invalid name.")

# print(result)