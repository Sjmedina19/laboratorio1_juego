import pygame


class LoadingScene:
    def __init__(self, screen_width, screen_height, next_scene_factory, duration=1.5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.next_scene_factory = next_scene_factory
        self.duration = duration
        self.elapsed = 0

        self.font_big = pygame.font.SysFont("arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("arial", 26)

    def handle_event(self, event):
        return None

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
           next_scene = self.next_scene_factory()

           if hasattr(next_scene, "on_resize"):
              next_scene.on_resize(self.screen_width, self.screen_height)

           return {
              "action": "finish_loading",
              "next_scene": next_scene
           }
        return None
    def draw(self, screen):
        screen.fill((10, 10, 20))

        title = self.font_big.render("Cargando mundo virtual...", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40)))

        dots = "." * (int(self.elapsed * 3) % 4)
        sub = self.font_small.render("Conectando" + dots, True, (180, 180, 220))
        screen.blit(sub, sub.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20)))