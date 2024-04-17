d = {
    "pipi": 0, "papa": 1, "dabi": 2
}

l = ["pipi", "dabi", "papa"]

l.sort(key = lambda item:d[item])

print(l)
