import time

questions = ("How tall are u?",
             "How heavy are u?",
             "How old are u?",
             "What's ur fav color?",
             "What's the name of the company u r aiming for?")

options = (("A. 150cm", "B. 160cm", "C. 170m", "D. 170cm"),
           ("A. 70kg", "B. 80kg", "C. 90kg", "D. 100kg"),
           ("A. 20y", "B. 21y", "C. 22y", "D. 23y"),
           ("A. Blue", "B. Black", "C. White", "D. Purple"),
           ("A. TSMC", "B. MediaTek", "C. ASE group", "D. Micron"))

answers = ("D", "A", "B", "C", "D")
guesses = []
counter = 0
score = 0
perc = 0

print("------------------------------------")
print("----- WELCOME TO THE QUIZ GAME -----")
print("------------------------------------")

time.sleep(1)

for question in questions:
    print(question)
    for option in options[counter]:
        print(option)

    guess = input("Pls enter the answer (A/B/C/D): ").upper()
    guesses.append(guess)
    
    if guess == answers[counter]:
        score += 1
        print("You got the CORRECT answer!")
    else:
        print("You got the WRONG answer!")
        print(f"{answers[counter]} is the correct answer.")

    counter += 1

print("------------------")
print("----- RESULT -----")
print("------------------")

print("Answer: ", end="")
for answer in answers:
    print(answer, end=" ")
print()

print("Guess: ", end="")
for guess in guesses:
    print(guess, end=" ")
print()

perc = int(score / len(questions) * 100)
print(f"Your score is {perc}%")