import pygame


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.color = (40, 80, 200)

        self.walk_speed = 220
        self.run_speed = 360

    def handle_movement(self, dt, keys, collision_rects):
        dx = 0
        dy = 0

        speed = self.run_speed if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else self.walk_speed

        if keys[pygame.K_a]:
            dx -= speed * dt
        if keys[pygame.K_d]:
            dx += speed * dt
        if keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_s]:
            dy += speed * dt

        self.move_and_collide(dx, dy, collision_rects)

    def move_and_collide(self, dx, dy, collision_rects):
        self.rect.x += int(dx)
        for wall in collision_rects:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        self.rect.y += int(dy)
        for wall in collision_rects:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, self.color, draw_rect)

        # pequeña “cabeza” para que se vea mejor
        head_rect = pygame.Rect(draw_rect.x + 6, draw_rect.y + 4, 20, 14)
        pygame.draw.rect(surface, (230, 220, 200), head_rect)