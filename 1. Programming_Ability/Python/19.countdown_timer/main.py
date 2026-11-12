import time 

timer = int(input("Pls enter the time: "))

x = "Hello."
x2 = "I'm ur personal assitant."

for x in range(timer, 0, -1):
    seconds = x % 60
    minutes = int(x / 60) % 60
    hours = int((x / 60) / 60) % 24
    print(f"{hours:02}:{minutes:02}:{seconds:02}")
    time.sleep(1)

print("TIME'S UP!")