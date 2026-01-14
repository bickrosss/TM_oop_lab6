# Базовая обработка исключений
print("start")
try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except Exception as e:
    print("Error! " + str(e))
print("stop")

# Обработка конкретных исключений
print("start")
try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except (ValueError, ZeroDivisionError):
    print("Error!")
print("stop")

# Раздельная обработка исключений
print("start")
try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except ValueError:
    print("ValueError!")
except ZeroDivisionError:
    print("ZeroDivisionError!")
except:
    print("Error!")
print("Stop")

# Обработка с получением объекта исключения
print("start")
try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except ValueError as ve:
    print("ValueError! {0}".format(ve))
except ZeroDivisionError as zde:
    print("ZeroDivisionError! {0}".format(zde))
except Exception as ex:
    print("Error! {0}".format(ex))
print("Stop")
