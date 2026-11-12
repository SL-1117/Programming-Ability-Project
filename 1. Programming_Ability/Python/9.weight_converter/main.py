weight = float(input("Pls enter ur weight in kg: "))
unit = input("Pls enter the unit u want to convert to (K/L): ")

if unit == "K":
    weight = weight * 2.20462
    unit = "pounds"
    print(f"Your weight is {round(weight, 2)} {unit}.")

elif unit == "L":
    weight = weight * 35.274
    unit = "ounces"
    print(f"Your weight is {round(weight, 2)} {unit}.")

else: 
    print("Invalid unit. Please enter 'K' for kilograms or 'L' for pounds.")