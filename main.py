import pygame
import sys


def main():
    pass


if __name__ == "__main__":
    pygame.init()
    try:
        main()
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        pygame.quit()
        sys.exit()
