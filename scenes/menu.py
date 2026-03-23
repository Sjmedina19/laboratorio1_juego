import pygame


class MenuScene:
    def __init__(self, screen_width, screen_height, message=""):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_option = pygame.font.SysFont("arial", 34)
        self.font_message = pygame.font.SysFont("arial", 24)

        self.options = [
            "Nueva partida",
            "Continuar",
            "Opciones",
            "Salir",
        ]

        self.selected = 0
        self.message = message

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)

            elif event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)

            elif event.key == pygame.K_RETURN:
                return self.execute_selected()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            for i in range(len(self.options)):
                rect = pygame.Rect(
                    self.screen_width // 2 - 170,
                    240 + i * 80,
                    340,
                    55
                )
                if rect.collidepoint(mx, my):
                    self.selected = i
                    return self.execute_selected()

        return None

    def execute_selected(self):
        option = self.options[self.selected]

        if option == "Nueva partida":
            return {"action": "new_game"}

        elif option == "Continuar":
            return {"action": "continue_game"}

        elif option == "Opciones":
            return {"action": "settings"}

        elif option == "Salir":
            return {"action": "quit"}

        return None

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 35))

        title = self.font_title.render("LABORATORIO 1", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.screen_width // 2, 120)))

        for i, option in enumerate(self.options):
            rect = pygame.Rect(
                self.screen_width // 2 - 170,
                240 + i * 80,
                340,
                55
            )

            color = (120, 80, 200) if i == self.selected else (220, 220, 220)
            text_color = (255, 255, 255) if i == self.selected else (20, 20, 20)

            pygame.draw.rect(screen, color, rect, border_radius=8)
            text = self.font_option.render(option, True, text_color)
            screen.blit(text, text.get_rect(center=rect.center))