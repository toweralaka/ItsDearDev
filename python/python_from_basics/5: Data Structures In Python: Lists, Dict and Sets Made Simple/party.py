guest_list = ["Tunde", "Chioma", "Ahmed", "Tunde", "Blessing",
              "Chioma", "Emeka", "Tunde"]

# for guest in guest_list:
#     print(f"Welcome {guest}!")

my_set = set()

# print("The set list")
unique_guest_list = set(guest_list)
# for guest in unique_guest_list:
#     print(f"Welcome {guest}!")


fun_friends = {"Tunde", "Chioma", "Ahmed", "Blessing", "Emeka"}
work_friends = {"Ahmed", "Blessing", "Kunle", "Zainab", "Ife"}

# intersect
close_friends = fun_friends & work_friends
# print(f"Close friends: {close_friends}")

# union
all_guests = fun_friends | work_friends
# print(f"Total unique guests: {len(all_guests)}")

fun_only = fun_friends - work_friends
# print(f"Fun friends only: {fun_only}")

all_guests.add("Folake")

all_guests.add("Kunle")

# print(all_guests)
# Check if someone is coming
# if "Tunde" in all_guests:
#     print("Tunde is coming!")

# - Removing duplicates from any list
# - Finding common items between groups
# - Checking if something exists(membership testing)
# - Unique tags, hashtags, or IDs"

guests = {
    "Tunde": {
        "phone": "0003-555-1234",
        "bringing": "Jollof Rice",
        "dietary": "None"
    },
    "Chioma": {
        "phone": "0001-555-5678",
        "bringing": "Small Chops",
        "dietary": "Vegetarian"
    },
    "Ahmed": {
        "phone": "0005-555-9012",
        "bringing": "Chapman",
        "dietary": "No peanuts"
    }
}
# print(guests["Tunde"]["phone"])
# print(guests["Chioma"]["bringing"])
guests["Blessing"] = {
    "phone": "0012-555-3456",
    "bringing": "Drinks",
    "dietary": "None"
}
# print(guests.keys())
guests["Tunde"]["bringing"] = "Fried Rice"