import pyautogui
import time

print("Pressione CTRL+C para sair.\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"X: {x}  Y: {y}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nPrograma encerrado.")