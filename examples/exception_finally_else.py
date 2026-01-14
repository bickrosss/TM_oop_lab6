# Пример с finally
try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except:
    print("Exception")
finally:
    print("Finally code")

# Пример с else
try:
    f = open("tmp.txt", "r")
    for line in f:
        print(line)
    f.close()
except Exception as e:
    print(e)
else:
    print("File was readed")

# Вложенные блоки с else
print("Program started")
try:
    print("Opening file...")
    f = open("data.txt", "w")
    try:
        print("Writing to file...")
        f.write("Hello World!")
    except Exception:
        print("Something gone wrong!")
    else:
        print("Success!")
except FileNotFoundError:
    print("File not found!")
print("Program finished")
