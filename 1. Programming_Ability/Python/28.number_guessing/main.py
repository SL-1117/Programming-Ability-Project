import random

answer = random.randint(1, 100)
lowest_Num = 1
highest_Num = 100
is_Running = True

print("==========================================")
print("========== Number Guessing Game ==========")
print("==========================================")

while is_Running:
    guess = input("Pls enter ur guess (1-100): ")

    if guess.isdigit():
        guess = int(guess)

        if guess < lowest_Num or guess > highest_Num:
            print("Invalid range.")
        elif guess > answer:
            print("Lower!")   
        elif guess < answer:
            print("Higher!")
        else:
            print("You answer is correct!")
            break

    else:
        print("You have to enter a valid num.")

