# Принудительная генерация исключения
try:
    raise Exception("Some exception")
except Exception as e:
    print("Exception exception " + str(e))

# Пользовательское исключение
class MegValException(Exception):
    pass

try:
    val = int(input("input positive number: "))
    if val < 0:
        raise MegValException("Neg val: " + str(val))
    print(val + 10)
except MegValException as e:
    print(e)
