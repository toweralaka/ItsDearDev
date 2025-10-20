guests_data = {}
confirmed = set()


def add_guest(name, phone, bringing, dietary="None"):
    """Add a guest to the party"""
    guests_data[name] = {
        "phone": phone,
        "bringing": bringing,
        "dietary": dietary,
        "confirmed": False
    }
    print(f"✅ {name} added to the list!")


def confirm_guest(name):
    """Mark guest as confirmed"""
    if name in guests_data:
        guests_data[name]["confirmed"] = True
        confirmed.add(name)  # Add to set!
        print(f"🎉 {name} confirmed!")
    else:
        print(f"❌ {name} is not on the guest list!")


def get_food_list():
    """See what everyone is bringing"""
    print("\n🍽️ FOOD FOR MY FUN PARTY:")
    food_items = set()

    for name, details in guests_data.items():
        if details["confirmed"]:
            food = details["bringing"]
            if food in food_items:
                print(
                    (
                        f"WARNING: {name} is bringing {food}, "
                        "but someone else already is!"))
            food_items.add(food)
            print(f"  - {name}: {food}")


def check_dietary_restrictions():
    """See who has dietary restrictions"""
    print("\n DIETARY RESTRICTIONS:")
    for name, details in guests_data.items():
        if details["confirmed"] and details["dietary"] != "None":
            print(f"  - {name}: {details['dietary']}")


def fun_summary():
    """Show party statistics"""
    total_guests = len(guests_data)
    confirmed_count = len(confirmed)

    print("\n PARTY SUMMARY")
    print(f"Total invited: {total_guests}")
    print(f"Confirmed: {confirmed_count}")
    print(f"Still waiting: {total_guests - confirmed_count}")
    print(f"Confirmed guests: {', '.join(confirmed)}")


add_guest("Tunde", "0003-555-1234", "Jollof Rice")
add_guest("Chioma", "0001-555-5678", "Small Chops", "Vegetarian")
add_guest("Ahmed", "0005-555-9012", "Chapman", "No peanuts")
add_guest("Blessing", "0012-555-3456", "Jollof Rice")

# Confirm some guests
confirm_guest("Tunde")
confirm_guest("Chioma")
confirm_guest("Blessing")


get_food_list()
check_dietary_restrictions()
fun_summary()

# TODO
# Add these features to the Party Planner:
# 1. A function to send reminders(print phone numbers)
# 2. Track RSVPs(who said yes, no, or maybe)
# 3. Calculate total food items
