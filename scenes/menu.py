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
        self.option_rects = []
        self.layout_dirty = True

    def on_resize(self, new_w, new_h):
        self.screen_width = new_w
        self.screen_height = new_h
        self.layout_dirty = True

    def update_layout(self):
        if not self.layout_dirty:
            return

        x = self.screen_width // 2 - 170
        start_y = max(180, self.screen_height // 3)
        self.option_rects = [
            pygame.Rect(x, start_y + i * 80, 340, 55)
            for i in range(len(self.options))
        ]
        self.layout_dirty = False

    def handle_event(self, event):
        self.update_layout()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(self.options)

            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(self.options)

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.execute_selected()

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            for i, rect in enumerate(self.option_rects):
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
        self.update_layout()
        screen.fill((20, 20, 35))

        title = self.font_title.render("LABORATORIO 1", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.screen_width // 2, 100)))

        for i, option in enumerate(self.options):
            rect = self.option_rects[i]
            color = (120, 80, 200) if i == self.selected else (220, 220, 220)
            text_color = (255, 255, 255) if i == self.selected else (20, 20, 20)

            pygame.draw.rect(screen, color, rect, border_radius=8)
            text = self.font_option.render(option, True, text_color)
            screen.blit(text, text.get_rect(center=rect.center))

        if self.message:
            msg = self.font_message.render(self.message, True, (255, 235, 130))
            msg_rect = msg.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
            screen.blit(msg, msg_rect)