import pygame
from pathlib import Path

class UI_variables:
    def __init__(self):
        # Fonts
        assets_path = Path(Path(__file__).parent.absolute(),"assets")
        fonts_path = Path(assets_path, "fonts") 
        self.font_path = Path(fonts_path, "OpenSans-Light.ttf")
        self.font_path_b = Path(fonts_path, "OpenSans-Bold.ttf")
        self.font_path_i = Path(fonts_path, "Inconsolata/Inconsolata.otf")

        self.h1 = pygame.font.Font(self.font_path, 50)
        self.h2 = pygame.font.Font(self.font_path, 30)
        self.h4 = pygame.font.Font(self.font_path, 20)
        self.h5 = pygame.font.Font(self.font_path, 13)
        self.h6 = pygame.font.Font(self.font_path, 10)

        self.h1_b = pygame.font.Font(self.font_path_b, 50)
        self.h2_b = pygame.font.Font(self.font_path_b, 30)

        self.h2_i = pygame.font.Font(self.font_path_i, 30)
        self.h5_i = pygame.font.Font(self.font_path_i, 13)

        # Sounds
        sounds_path = Path(assets_path, "sounds")
        self.click_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_ButtonUp.wav"))
        self.move_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_PieceMoveLR.wav"))
        self.drop_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_PieceHardDrop.wav"))
        self.single_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_SpecialLineClearSingle.wav"))
        self.double_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_SpecialLineClearDouble.wav"))
        self.triple_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_SpecialLineClearTriple.wav"))
        self.tetris_sound = pygame.mixer.Sound(Path(sounds_path, "SFX_SpecialTetris.wav"))

        # Background colors
        self.black = (10, 10, 10) #rgb(10, 10, 10)
        self.white = (255, 255, 255) #rgb(255, 255, 255)
        self.grey_1 = (26, 26, 26) #rgb(26, 26, 26)
        self.grey_2 = (35, 35, 35) #rgb(35, 35, 35)
        self.grey_3 = (55, 55, 55) #rgb(55, 55, 55)

        # Tetrimino colors
        self.cyan = (69, 206, 204) #rgb(69, 206, 204) # I
        self.blue = (64, 111, 249) #rgb(64, 111, 249) # J
        self.orange = (253, 189, 53) #rgb(253, 189, 53) # L
        self.yellow = (246, 227, 90) #rgb(246, 227, 90) # O
        self.green = (98, 190, 68) #rgb(98, 190, 68) # S
        self.pink = (242, 64, 235) #rgb(242, 64, 235) # T
        self.red = (225, 13, 27) #rgb(225, 13, 27) # Z

        self.t_color = [self.grey_2, self.cyan, self.blue, self.orange, self.yellow, self.green, self.pink, self.red, self.grey_3]