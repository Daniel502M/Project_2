import pygame


def load_animations():
    walt_Down = [
        pygame.image.load(f'assets/Animation/Running/Down/Human_Animations_{i}.png').convert_alpha()
        for i in range(37, 43)
    ]
    walt_Left = [
        pygame.image.load(f'assets/Animation/Running/Left/Human_Animations_{i}.png').convert_alpha()
        for i in range(19, 25)
    ]
    walt_Right = [
        pygame.image.load(f'assets/Animation/Running/Right/Human_Animations_{i}.png').convert_alpha()
        for i in range(13, 19)
    ]
    walt_Up = [
        pygame.image.load(f'assets/Animation/Running/Up/Human_Animations_{i}.png').convert_alpha()
        for i in range(43, 49)
    ]
    walt_lower_left = [
        pygame.image.load(f'assets/Animation/Running/Lower_Left/Human_Animations_{i}.png').convert_alpha()
        for i in range(31, 37)
    ]
    walt_lower_right = [
        pygame.image.load(f'assets/Animation/Running/Lower_Right/Human_Animations_{i}.png').convert_alpha()
        for i in range(25, 31)
    ]
    walt_upper_left = [
        pygame.image.load(f'assets/Animation/Running/Upper_Left/Human_Animations_{i}.png').convert_alpha()
        for i in range(7, 13)
    ]
    walt_upper_right = [
        pygame.image.load(f'assets/Animation/Running/Upper_Right/Human_Animations_{i}.png').convert_alpha()
        for i in range(1, 7)
    ]
    return {"down": walt_Down, "left": walt_Left, "right": walt_Right, "up": walt_Up, \
            "lower_left": walt_lower_left, "lower_right": walt_lower_right, \
            "upper_left": walt_upper_left, "upper_right": walt_upper_right}


def load_attack_animation(direction):
    walt_Right = [
        pygame.image.load(f'assets/Animation/Attack/{direction}/Human_Animations_{i}.png').convert_alpha()
        for i in range(1, 5)
    ]
    walt_Left = [
        pygame.image.load(f'assets/Animation/Attack/{direction}/Human_Animations_{i}.png').convert_alpha()
        for i in range(1, 5)
    ]
    walt_Down = [
        pygame.image.load(f'assets/Animation/Attack/{direction}/Human_Animations_{i}.png').convert_alpha()
        for i in range(1, 5)
    ]
    walt_Up = [
        pygame.image.load(f'assets/Animation/Attack/{direction}/Human_Animations_{i}.png').convert_alpha()
        for i in range(1, 5)
    ]
    return {"left": walt_Left, "right": walt_Right, "down": walt_Down, "up": walt_Up}


