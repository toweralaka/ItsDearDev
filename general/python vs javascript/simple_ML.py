# A very simplified example of Machine Learning (ML):

# Step 1: Training data (examples the program learns from)
fruits = ["apple", "banana", "apple", "banana", "apple"]
colors = ["red", "yellow", "green", "yellow", "red"]

# Step 2: Teach the program by matching fruit with color
fruit_knowledge = {}
for fruit, color in zip(fruits, colors):
    fruit_knowledge[color] = fruit
# program learns "red = apple", "yellow = banana", etc.


# Step 3: Now let’s ask the program to guess
def guess_fruit(color):
    return fruit_knowledge.get(color, "I don't know this fruit yet!")


# Testing the program
print(guess_fruit("red"))     # → apple
print(guess_fruit("yellow"))  # → banana
print(guess_fruit("green"))   # → apple
print(guess_fruit("purple"))  # → I don't know this fruit yet!
