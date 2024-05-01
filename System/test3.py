n = int(input())
l = list(map(int, input().split()))

c = [[None]*n for x in range(n)] # [i][j]為合併最小花費
v = [[None]*n for x in range(n)]

for i in range(n):
    for j in range(i, n):
        if i == j:
            v[i][j] = l[i]
        else:
            v[i][j] = v[i][j - 1] + l[j]

for i in range(n):
    c[i][i] = 0

for d in range(2, n + 1):
    for i in range(0, n - d + 1):
        j = i + d - 1
        c[i][j] = float("inf")
        for k in range(i, j):
            c[i][j] = min(c[i][j], c[i][k] + c[k + 1][j] + abs(v[i][k]-v[k+1][j]))

print(c[0][n-1])
