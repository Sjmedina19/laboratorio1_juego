import pygame


class SettingsScene:
    def __init__(self, screen_width, screen_height, settings, available_resolutions):
        self.w = screen_width
        self.h = screen_height

        self.font_title = pygame.font.SysFont("arial", 54, bold=True)
        self.font = pygame.font.SysFont("arial", 30)
        self.small = pygame.font.SysFont("arial", 22)

        self.settings = settings.copy()
        self.available_resolutions = available_resolutions

        self.options = [
            "Volumen Música",
            "Silenciar Música",
            "Volumen SFX",
            "Silenciar SFX",
            "Resolución",
            "Fullscreen",
            "Volver"
        ]

        self.selected = 0

    def get_resolution_text(self):
        w, h = self.available_resolutions[self.settings["resolution_index"]]
        return f"{w}x{h}"

    def toggle_option(self, option):
        if option == "Silenciar Música":
            self.settings["mute_music"] = not self.settings["mute_music"]

        elif option == "Silenciar SFX":
            self.settings["mute_sfx"] = not self.settings["mute_sfx"]

        elif option == "Fullscreen":
            self.settings["fullscreen"] = not self.settings["fullscreen"]

    def change_value(self, direction):
        option = self.options[self.selected]

        if option == "Volumen Música":
            self.settings["music_volume"] = max(
                0, min(100, self.settings["music_volume"] + direction * 5)
            )
            return {"action": "preview_settings", "settings": self.settings}

        elif option == "Volumen SFX":
            self.settings["sfx_volume"] = max(
                0, min(100, self.settings["sfx_volume"] + direction * 5)
            )
            return {"action": "preview_settings", "settings": self.settings}

        elif option == "Resolución":
            # SOLO cambia resolución si no está en fullscreen
            if not self.settings["fullscreen"]:
                self.settings["resolution_index"] = (
                    self.settings["resolution_index"] + direction
                ) % len(self.available_resolutions)
                return {"action": "preview_settings", "settings": self.settings}

        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)

            elif event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)

            elif event.key == pygame.K_a:
                result = self.change_value(-1)
                if result:
                    return result

            elif event.key == pygame.K_d:
                result = self.change_value(1)
                if result:
                    return result

            elif event.key == pygame.K_RETURN:
                option = self.options[self.selected]

                if option in ["Silenciar Música", "Silenciar SFX", "Fullscreen"]:
                    self.toggle_option(option)
                    return {"action": "preview_settings", "settings": self.settings}

                elif option == "Volver":
                    return {"action": "back_from_settings", "settings": self.settings}

            elif event.key == pygame.K_ESCAPE:
                return {"action": "back_from_settings", "settings": self.settings}

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.w // 2 - 260, 180 + i * 70, 520, 50)

                if rect.collidepoint(mx, my):
                    self.selected = i
                    option_name = self.options[i]

                    if option_name == "Volver":
                        return {"action": "back_from_settings", "settings": self.settings}

                    elif option_name in ["Silenciar Música", "Silenciar SFX", "Fullscreen"]:
                        self.toggle_option(option_name)
                        return {"action": "preview_settings", "settings": self.settings}

                    elif option_name in ["Volumen Música", "Volumen SFX", "Resolución"]:
                        result = self.change_value(1)
                        if result:
                            return result

        return None

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((30, 30, 55))

        title = self.font_title.render("OPCIONES", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.w // 2, 90)))

        for i, option in enumerate(self.options):
            rect = pygame.Rect(self.w // 2 - 260, 180 + i * 70, 520, 50)
            color = (120, 80, 200) if i == self.selected else (220, 220, 220)
            text_color = (255, 255, 255) if i == self.selected else (20, 20, 20)

            pygame.draw.rect(screen, color, rect, border_radius=8)

            value = ""
            if option == "Volumen Música":
                value = f": {self.settings['music_volume']}"
            elif option == "Silenciar Música":
                value = f": {'ON' if self.settings['mute_music'] else 'OFF'}"
            elif option == "Volumen SFX":
                value = f": {self.settings['sfx_volume']}"
            elif option == "Silenciar SFX":
                value = f": {'ON' if self.settings['mute_sfx'] else 'OFF'}"
            elif option == "Resolución":
                value = f": {self.get_resolution_text()}"
            elif option == "Fullscreen":
                value = f": {'ON' if self.settings['fullscreen'] else 'OFF'}"

            text = self.font.render(option + value, True, text_color)
            screen.blit(text, text.get_rect(center=rect.center))

        hint = self.small.render(
            "W/S navega - A/D cambia - ENTER alterna - mouse también funciona",
            True,
            (220, 220, 220)
        )
        screen.blit(hint, hint.get_rect(center=(self.w // 2, self.h - 50)))