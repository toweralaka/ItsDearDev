# condition
# repetition
# interuptions

# allowed_age = 18
# age = 12
# with_parent = False

# if age > 18:
#     print("Welcome In!")
# elif with_parent is True:
#     print("Welcome In With Parent!")
# else:
#     print("You are not allowed in")


# for name in ["Susan", "Bisi", "Chika", "Awa"]:
#     print(name)

# age = 2
# while age < 19:
#     print("Go home")
#     age += 1


name_list = ["Susan", "Omo", "Bisi", "Chika", "Awa", "Ben"]
for name in name_list:
    if name == "Chika":
        continue
    elif name == "Omo":
        print(f"Oh no, {name} is here, party over")
        break
    print(f"Welcome to the party, {name}!")


# Write a while loop that welcomes people
# to your party until the length of
# name_list is 21
