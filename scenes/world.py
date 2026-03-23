import pygame
import os


class WorldScene:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font = pygame.font.SysFont("arial", 28)

        path = os.path.join("assets", "bedroom.png")
        self.background = pygame.image.load(path).convert()
        self.background = pygame.transform.scale(
            self.background, (screen_width, screen_height)
        )

        self.player = pygame.Rect(560, 500, 40, 55)
        self.speed = 250

        self.pc_rect = pygame.Rect(300, 300, 150, 100)

        self.message = ""
        self.message_timer = 0

        self.paused = False
        self.pause_options = [
            "Continuar",
            "Opciones",
            "Guardar",
            "Guardar y salir",
            "Salir sin guardar"
        ]
        self.pause_selected = 0

    def on_resize(self, new_w, new_h):
        self.screen_width = new_w
        self.screen_height = new_h

        path = os.path.join("assets", "bedroom.png")
        self.background = pygame.image.load(path).convert()
        self.background = pygame.transform.scale(
            self.background, (new_w, new_h)
        )

        self.pc_rect = pygame.Rect(300, 300, 150, 100)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
                return None

            if self.paused:
                if event.key == pygame.K_w:
                    self.pause_selected = (self.pause_selected - 1) % len(self.pause_options)

                elif event.key == pygame.K_s:
                    self.pause_selected = (self.pause_selected + 1) % len(self.pause_options)

                elif event.key == pygame.K_RETURN:
                    return self.execute_pause_option()

            else:
                if event.key == pygame.K_e:
                    if self.player.colliderect(self.pc_rect):
                        return {"action": "start_loading_virtual_world"}

        return None

    def execute_pause_option(self):
        option = self.pause_options[self.pause_selected]

        if option == "Continuar":
            self.paused = False

        elif option == "Opciones":
            return {"action": "settings"}

        elif option == "Guardar":
            return {"action": "save_game"}

        elif option == "Guardar y salir":
            return {"action": "save_and_menu"}

        elif option == "Salir sin guardar":
            return {"action": "menu_without_save"}

        return None

    def update(self, dt):
        if self.paused:
            return

        keys = pygame.key.get_pressed()

        speed = self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed *= 1.8

        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_s]:
            dy += speed * dt
        if keys[pygame.K_a]:
            dx -= speed * dt
        if keys[pygame.K_d]:
            dx += speed * dt

        self.player.x += int(dx)
        self.player.y += int(dy)

        self.player.x = max(0, min(self.player.x, self.screen_width - self.player.width))
        self.player.y = max(0, min(self.player.y, self.screen_height - self.player.height))

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def get_save_data(self):
        return {
            "scene": "bedroom",
            "x": self.player.x,
            "y": self.player.y
        }

    def load_save_data(self, data):
        self.player.x = data.get("x", 500)
        self.player.y = data.get("y", 500)

    def show_message(self, text, duration=2):
        self.message = text
        self.message_timer = duration

    def draw_pause(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        for i, option in enumerate(self.pause_options):
            color = (255, 255, 255) if i == self.pause_selected else (150, 150, 150)
            text = self.font.render(option, True, color)
            screen.blit(text, (self.screen_width // 2 - 120, 220 + i * 60))

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        pygame.draw.rect(screen, (220, 60, 60), self.player)

        if self.player.colliderect(self.pc_rect):
            text = self.font.render("E para usar PC", True, (255, 255, 0))
            screen.blit(text, (20, self.screen_height - 60))

        if self.message:
            text = self.font.render(self.message, True, (255, 255, 255))
            screen.blit(text, (400, 650))

        if self.paused:
            self.draw_pause(screen)