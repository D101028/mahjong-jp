upper = 3
class Test():
    def __init__(self):
        pass 
    def func(self):
        print("origin")
finalclass = Test

for i in range(upper):
    if i == 0:
        class TempClass(finalclass):
            def __init__(self):
                super().__init__()
            def func0(self):
                print("0")
        finalclass = TempClass
    elif i == 1:
        class TempClass(finalclass):
            def __init__(self):
                super().__init__()
            def func1(self):
                print("1")
        finalclass = TempClass
    elif i == 2:
        class TempClass(finalclass):
            def __init__(self):
                super().__init__()
            def func2(self):
                print("2")
        finalclass = TempClass
    elif i == 3:
        class TempClass(finalclass):
            def __init__(self):
                super().__init__()
            def func3(self):
                print("3")
        finalclass = TempClass
    elif i == 4:
        class TempClass(finalclass):
            def __init__(self):
                super().__init__()
            def func4(self):
                print("4")
        finalclass = TempClass

# finalclass().func4()


