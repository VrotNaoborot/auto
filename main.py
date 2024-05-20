import subprocess
import os
import time
import random

import uiautomator2 as ua2

package_name_atx = "com.github.uiautomator"
# adb_path = "/home/user1/android-sdk/platform-tools/adb"
adb_path = "/Users/panu/Applications/platform-tools/adb"
package_name_tg = "org.telegram.messenger.web"
project_path = os.getcwd()


def clicker(device):
    time.sleep(3)
    print("Погнали кликать")
    while True:
        for i in range(600):
            device.click(random.uniform(0.27, 0.65), random.uniform(0.621, 0.803))
        print("Спим 30 минут")
        time.sleep(1800)


def open_miniapp(device):
    while True:
        print("Открытие приложения..")
        group_views = device(className="android.view.ViewGroup")
        if group_views.exists:
            first_group_view = group_views[0]  # Выбор первого элемента
            first_group_view.click()
            print("Click Hamster Kombat")
        if device.xpath('//*[@text="Играть в 1 клик .."]').click_exists(0.1):
            print("Играть в 1 клик")
        if device.xpath('//*[@text="To launch this web app, you will connect to its website."]').wait(0.1):
            device.xpath('//*[@text="Start"]').click_exists()
            print("Start")
        # проверка на открытие
        if device.xpath('//*[@content-desc="Go back"]').wait(0.1) and device.xpath(
                '//*[@text="Hamster Kombat"]').wait(0.1) and device.xpath(
            '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]').wait(
            0.1) and device.xpath(
            '//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]').wait(
            0.1):
            print("Приложение открыто!")
            return True
        device.click(0.364, 0.018)


def auth_account(device):
    """Авторизация аккаунта телеграмм"""
    print("Авторизация аккаунта..")
    while True:
        if device.xpath(
                '//*[@text="Telegram needs access to your contacts so that you can connect with your friends across all your devices. Your contacts will be continuously synced with Telegram\'s heavily encrypted cloud servers."]').wait(
            0.1):
            device.xpath('//*[@text="Continue"]').click()

        if device.xpath('//*[@text="Start Messaging"]').click_exists(timeout=0.1):
            print("Start messaging")
        if device.xpath(
                '//*[@text="Please allow Telegram to receive calls so that we can automatically confirm your phone number."]').wait(
            0.1):
            device.xpath('//*[@text="Continue"]').click()
            print("Continue")

        if device.xpath('//*[@resource-id="com.android.permissioncontroller:id/permission_message"]').wait(0.1):
            device.xpath('//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]').click()

        if device.xpath('//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]').click_exists(
                timeout=0.1):
            print("Разрешить")

        edit_text_1 = device(className="android.widget.EditText", instance=0)
        if edit_text_1.wait(0.1):
            edit_text_2 = device(className="android.widget.EditText", instance=1)
            edit_text_1.clear_text()
            edit_text_2.clear_text()
            edit_text_1.send_keys("+7")
            edit_text_2.send_keys("9278865751")
        if device.xpath('//*[@content-desc="Done"]').click_exists(timeout=0.1):
            print("Done")
        if device.xpath('//*[@text="Check your Telegram messages"]').wait(timeout=0.1):
            # Запрашиваем у пользователя ввод кода
            code = input("Введите код: \n")

            # Находим все элементы типа EditText
            edit_texts = device(className="android.widget.EditText")

            # Убедимся, что найдено как минимум 5 элементов
            if len(edit_texts) == 5:
                # Очищаем текст и вводим код в первые пять найденных элементов EditText
                for i in range(5):
                    edit_text = edit_texts[i]
                    edit_text.clear_text()  # Очищаем текст

                for j in range(5):
                    edit_texts[j].send_keys(code[j])
                    print(code[j])
                    time.sleep(1)
            else:
                print(f"Ожидалось 5 элементов EditText, но найдено {len(edit_texts)}")
        if device.xpath('//*[@content-desc="Open navigation menu"]').wait(0.1):
            print("Авторизация выполнена")
            return True
        if device.xpath('//*[@content-desc="Go back"]').click_exists(0.1):
            print("Back")


def is_app_installed(package_name, emulator_serial):
    adb_command = [adb_path, "-s", emulator_serial, "shell", "pm", "list",
                   "packages"]
    result = subprocess.run(adb_command, capture_output=True, text=True)
    if package_name in result.stdout:
        return True
    else:
        return False


def install_app(device, apk_path):
    try:
        # Установка приложения
        device.app_install(apk_path)
        print("Приложение установлено успешно")
        return True
    except Exception as ex:
        print(f"Ошибка при установке: {ex}")
        return False


def main():
    try:
        # device_name = input("Введите название девайса: \n")
        device_name = input("Введите название эмулятора: \n")
        if is_app_installed(package_name_atx, device_name):
            print(f"Обнаружено приложение ATX.")
            try:
                subprocess.run([adb_path, "-s", device_name, "shell", "pm", "uninstall", package_name_atx],
                               check=True)
                print("ATX приложение успешно удалено.")
            except subprocess.CalledProcessError:
                print("Не удалось удалить ATX приложение.")

        print("Подключение к девайсу...")
        device = ua2.connect(device_name)

        print("Проверка приложения Telegram")
        if is_app_installed(package_name_tg, device_name):
            print("Телеграмм уже установлен на устройстве.")
        else:
            print("Телеграмм не установлен. Начинаем процесс установки...")
            if not install_app(device, project_path + "/Telegram.apk"):
                return -1
        print("Запуск телеграмм")

        device.app_start(package_name_tg)

        # Проверка состояния приложения
        if device.app_wait(package_name_tg, front=True, timeout=10):
            print(f"Приложение {package_name_tg} активно и готово к взаимодействию")

            if not device.xpath('//*[@content-desc="Open navigation menu"]').wait(0.5):
                auth_account(device)
            open_miniapp(device)
        else:
            print(f"Приложение {package_name_tg} не удалось запустить или оно не активно")

        clicker(device)

    except Exception as ex:
        print(f"Ошибка: {ex}")


if __name__ == "__main__":
    main()
