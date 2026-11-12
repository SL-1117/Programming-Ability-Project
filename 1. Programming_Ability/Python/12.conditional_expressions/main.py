# char name_check[30] = "";
# printf("%s", name_check[0] 
#       ? "You didn't enter ur name." 
#       : "You entered ur name.");

num = 3
num2 = 1
age = 17
temperature = 30
user_role = "Admin"

user_role = user_role.lower()

# print("Positive" if num > 0 else "Negative")
# result = "EVEN" if num % 2 == 0 else "ODD"
# max_num = num2 if num2 > num else num
# min_num = num2 if num2 < num else num
# status = "Adult" if age >= 18 else "Kid"
# weather = "Hot" if temperature > 40 else "normal"
access_level = "Full access" if user_role == "admin" else "limited access"

print(access_level)
