# # membership operators = used to tes twhether a value or variable is found in a sequence
#                         (string, list, tuple, set, or, dictionary)
#                         1. in
#                         2. not in

# word = "Pineapple"

# guess = input("Enter: ")

# if guess in word:
#     print("Y")
# else:
#     print("N")


# students = {"SpongeBob", "Patrick", "Squarepants", "Sandy"}

# student = input("Enter the student name: ")

# if student not in students:
#     print(f"{student} was not found")
# else:
#     print(f"{student} is found")


grades = {"SpongeBob": 90,
          "Patrick": 100, 
          "Sandy": 98,
          "Crab boss": 90}

student = input("Enter the name of the student: ").capitalize()

if student in grades:
    print(f"{student}'s grade is {grades[student]}")
else:
    print(f"{student} wass not found.")

email = "Bro1117@gmail.com"



if "@" in email and "." in email:
    print("Valid email")
else:
    print("Invalid email")