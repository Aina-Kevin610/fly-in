import pygame
import sys
from parsing import Parser, ParseError, Any


class Visuel:
    def __init__(self, data: dict[str, Any]):
        self.data = data
        # self.coordinate = 

        pygame.init()
        self.width, self.height = 1900, 1000

        self.screen = pygame.display.set_mode((1900, 1000))

        pygame.display.set_caption("Mon premier jeu")
        self.font  = pygame.font.Font(None, 50)

        self.running = True
    
    def visual(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((30, 30, 30))
            # text = self.font.render(HUB[0]["x"], True, (255, 255, 255))
            # self.screen.blit(text, (100, 100))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        data = parser.parse()
        from pprint import pprint
        pprint(data)
        test = Visuel(data)
        test.visual()
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)