names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate adds index to each element
for index, name in enumerate(names):
    print(index, name)

print()

# zip pairs elements from two lists
for name, score in zip(names, scores):
    print(name, score)  