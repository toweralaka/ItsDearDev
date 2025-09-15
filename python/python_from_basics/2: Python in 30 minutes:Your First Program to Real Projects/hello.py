# print statement to write to the terminal
print("Hello world")
# variables to collection user information
x = "Ola"  # Dont use this variable names, make it clearer!
name = "Ola"
age = 9
hobbies = ["movies", "reading", "baking"]
print(f"{x} is {age} years old")

# conditional statement
if age >= 9:
    print("welcome")
    print("nice to have you!")
else:
    print("too young")

# for loop replaces this
print(name)
print(name)
print(name)
print(name)
print(name)
print(name)
print(name)
print(name)
print(name)

# for loop
for i in range(0, age):
    print(name)

# print_double_square function replaces this
print(2+2)
print(2*2)
print(3+3)
print(3*3)


def print_double_square(number):
    print(number+number)
    print(number*number)


print_double_square(9)


# Apply what we learnt
# Write a function that prints the square
# of a number from 0 to the given number
