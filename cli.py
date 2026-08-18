import pyautogui
import keyboard
import threading
import time

rodando = False

def macro():
    global rodando

    while rodando:

        pyautogui.click(1697,194)
        time.sleep(3)

        pyautogui.click(2148,210)
        time.sleep(3)

        pyautogui.click(1973,158)
        time.sleep(3)

        pyautogui.write("abastece v4 - nov")
        time.sleep(3)

        pyautogui.click(1884,174)
        time.sleep(3)

        pyautogui.click(2381,402)
        time.sleep(3)


def iniciar():
    global rodando

    if not rodando:
        rodando = True
        threading.Thread(target=macro, daemon=True).start()
        print("Macro iniciada")


def parar():
    global rodando
    rodando = False
    print("Macro parada")


keyboard.add_hotkey("F8", iniciar)
keyboard.add_hotkey("F9", parar)

print("F8 = Iniciar")
print("F9 = Parar")

keyboard.wait()