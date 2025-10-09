# Script: steps to feed a pet 🐱
def feed_pet():
    print("Open the food bag")
    print("Pour food into the bowl")
    print("Call the cat to eat")


# Automation: do it every day without reminding
for day in range(1, 8):  # one week
    print(f"Day {day}:")
    feed_pet()
    print("---")
