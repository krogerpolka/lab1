words = ["so", "black", "GOOD", "cricket"]
sorted_words= sorted(words, key=lambda x: len(x)) # can use a lambda as a key for custom sorting
print(sorted_words)
