import pygame
import sys

from menu import main_menu, settings_menu
from game import game_loop, start_new_game


def main():
    """
        Основной цикл игры, управляющий состояниями: меню, игра, настройки.
        """
    state = "menu"  # Начальное состояние
    while True:
        if state == "menu":
            state = main_menu()  # Возвращает следующее состояние: "game", "settings" или завершает программу
        elif state == "settings":
            state = settings_menu()  # После настроек возвращаемся в меню
        elif state == "game":
            start_new_game()  # Запускает игру
            game_loop()

            state = "menu"  # Возвращаемся в меню после завершения игры
        else:
            print("Неизвестное состояние:", state)
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    pygame.init()
    try:
        main()
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        pygame.quit()
        sys.exit()
