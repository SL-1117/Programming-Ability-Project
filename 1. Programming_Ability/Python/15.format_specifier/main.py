# printf("|Level: %-11d|\n", level);
# printf("|HP:    %-11.2f|\n", hp);
# printf("|MP:    %-11.2lf|", mp);

level = 92.97882
level_2 = 98.478
level_3 = -99.99

level = 111888992.97882
level_2 = 998.478
level_3 = -1099.99

# print(f"{level:^20}")
# print(f"{level_2:>10}")
# print(f"{level_3:<10}")

# print(f"Your level is #{level:+}")
# print(f"Your level is #{level_2:+}")
# print(f"Your level is #{level_3:+}")

# print(f"Your level is #{level: }")
# print(f"Your level is #{level_2: }")
# print(f"Your level is #{level_3: }")

print(f"Your level is #{level:+,.3f}")
print(f"Your level is #{level_2:+,.3f}")
print(f"Your level is #{level_3:+,.3f}")