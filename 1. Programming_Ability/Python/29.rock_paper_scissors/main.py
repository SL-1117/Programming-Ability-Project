import random 

options = ["Rock", "Paper", "Scissors"]
is_Running = True

while is_Running:

    player = None
    computer = random.choice(options)

    while player not in options:
        player = input("Enter the option: ").capitalize()

    print(f"Player: {player}")
    print(f"Computer: {computer}")

    if player == computer:
        print("It's a tie!")
    elif player == "Scissor" and computer == "Paper":
        print("You win!")
    elif player == "Rock" and computer == "Scissors":
        print("You win!")
    elif player == "Paper" and computer == "Rock":
        print("You win!")
    else:
        print("You lose!")

    if not input("Would u like to player again? (y/n): ").lower() == "y":
        print("Thanks for playing!")
        is_Running = False
