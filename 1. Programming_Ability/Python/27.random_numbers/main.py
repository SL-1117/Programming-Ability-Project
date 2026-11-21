import random

options = ("Rock", "Paper", "Scissors")

cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

number = random.randint(1, 6)
computer_Option = random.choice(options)
random.shuffle(cards)

print(computer_Option)
print(cards)

print(number)