import uiautomator2 as u2

device = u2.connect(input("Введите название эмулятора"))

print(device.info)