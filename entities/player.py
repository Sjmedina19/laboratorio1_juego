import os
import pygame


class Player:
    def __init__(self, x, y, character_folder="hero", frame_w=32, frame_h=48, scale=2):
        self.rect = pygame.Rect(x, y, frame_w * scale, frame_h * scale)
        self.color = (40, 80, 200)

        self.walk_speed = 220
        self.run_speed = 360

        self.direction = "down"
        self.moving = False
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.12

        self.animations = {}
        self._load_animations(character_folder, frame_w, frame_h, scale)

    def _load_animations(self, character_folder, frame_w, frame_h, scale):
        base = os.path.join("assets", "images", "characters", character_folder)
        directions = ["down", "up", "left", "right"]

        for direction in directions:
            frames = []
            for i in range(4):
                path = os.path.join(base, f"{direction}_{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (frame_w * scale, frame_h * scale))
                    frames.append(img)
            self.animations[direction] = frames

    def handle_movement(self, dt, keys, collision_rects, world_width, world_height):
        dx = 0.0
        dy = 0.0
        self.moving = False

        speed = self.run_speed if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else self.walk_speed

        if keys[pygame.K_a]:
            dx -= speed * dt
            self.direction = "left"
            self.moving = True
        if keys[pygame.K_d]:
            dx += speed * dt
            self.direction = "right"
            self.moving = True
        if keys[pygame.K_w]:
            dy -= speed * dt
            self.direction = "up"
            self.moving = True
        if keys[pygame.K_s]:
            dy += speed * dt
            self.direction = "down"
            self.moving = True

        self.move_and_collide(dx, dy, collision_rects)

        self.rect.x = max(0, min(self.rect.x, world_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, world_height - self.rect.height))

        self.update_animation(dt)

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

    def update_animation(self, dt):
        frames = self.animations.get(self.direction, [])
        if not frames:
            return

        if self.moving:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(frames)
        else:
            self.frame_index = 0

    def draw(self, surface, to_screen=None):
        draw_rect = self.rect
        if callable(to_screen):
            draw_rect = to_screen(self.rect)
        elif to_screen is not None and hasattr(to_screen, "apply"):
            draw_rect = to_screen.apply(self.rect)

        frames = self.animations.get(self.direction, [])
        if frames:
            image = frames[self.frame_index % len(frames)]
            surface.blit(image, draw_rect)
            return

        pygame.draw.rect(surface, self.color, draw_rect)
        head_rect = pygame.Rect(draw_rect.x + 6, draw_rect.y + 4, 20, 14)
        pygame.draw.rect(surface, (230, 220, 200), head_rect)