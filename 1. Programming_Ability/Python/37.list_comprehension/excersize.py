# ex


nums = [1, -2, 3, -4, 5, 6]
positive_nums = [positive for positive in nums if positive >= 0]
negative_nums = [negative for negative in nums if negative < 0]
even_nums = [enum for enum in nums if enum % 2 == 0]
odd_nums = [onum for onum in nums if onum % 2 == 1]

print(positive_nums, negative_nums, even_nums, odd_nums)



grades = [85, 42, 79, 90, 56, 61, 30]

passing_grades = [grade for grade in grades if grade >= 60]
print(passing_grades)