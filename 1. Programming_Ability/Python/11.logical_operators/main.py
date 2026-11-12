# ||, &&, !

raining = False
temperature = 30
humidity = 85

if raining or temperature < 0 or humidity > 90 or humidity < 20:
    print("The outdoor event is cancelled.")

elif not raining and temperature >= 30 and humidity <= 80 and humidity >= 20:
    print("It's an excellent day for the outdoor event.")

else: 
    print("The outdoor event is on (not a good weather tho).")