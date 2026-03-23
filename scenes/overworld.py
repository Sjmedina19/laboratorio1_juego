import pygame


class OverworldScene:
    class DialogueBox:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.font = pygame.font.SysFont("arial", 20)
            self.title_font = pygame.font.SysFont("arial", 22, bold=True)

            self.active = False
            self.lines = []
            self.index = 0
            self.speaker = ""

        def on_resize(self, new_w, new_h):
            self.width = new_w
            self.height = new_h

        def start(self, speaker, lines):
            self.speaker = speaker
            self.lines = list(lines) if lines else [""]
            self.index = 0
            self.active = True

        def advance(self):
            if not self.active:
                return

            self.index += 1
            if self.index >= len(self.lines):
                self.active = False
                self.index = 0

        def wrap_text(self, text, max_width):
            if text is None:
                return [""]

            paragraphs = str(text).split("\n")
            wrapped_lines = []

            for paragraph in paragraphs:
                words = paragraph.split()
                if not words:
                    wrapped_lines.append("")
                    continue

                current = words[0]

                for word in words[1:]:
                    test = current + " " + word
                    if self.font.size(test)[0] <= max_width:
                        current = test
                    else:
                        wrapped_lines.append(current)
                        current = word

                if current:
                    wrapped_lines.append(current)

            return wrapped_lines if wrapped_lines else [""]

        def draw(self, screen):
            if not self.active:
                return

            box = pygame.Rect(40, self.height - 180, self.width - 80, 140)
            pygame.draw.rect(screen, (20, 20, 30), box, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), box, 2, border_radius=10)

            title = self.title_font.render(self.speaker, True, (255, 220, 120))
            screen.blit(title, (box.x + 15, box.y + 10))

            text = self.lines[self.index] if 0 <= self.index < len(self.lines) else ""
            wrapped = self.wrap_text(text, box.width - 30)

            max_lines = max(1, (box.height - 60) // 22)
            wrapped = wrapped[:max_lines]

            y = box.y + 45
            for line in wrapped:
                txt = self.font.render(line, True, (255, 255, 255))
                screen.blit(txt, (box.x + 15, y))
                y += 22

            hint = self.font.render("E → continuar", True, (180, 180, 180))
            screen.blit(hint, (box.right - 150, box.bottom - 25))

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paused = False
        self.pause_options = [
            "Continuar",
            "Opciones",
            "Guardar",
            "Guardar y salir",
            "Salir sin guardar"
        ]
        self.pause_selected = 0

        self.world_width = 3000
        self.world_height = 2000

        self.player = pygame.Rect(400, 1700, 40, 50)
        self.player_fx = float(self.player.x)
        self.player_fy = float(self.player.y)

        self.speed = 250
        self.run_speed = 420
        self.direction = "down"

        self.cam_x = 0
        self.cam_y = 0

        self.dialogue = self.DialogueBox(width, height)

        self.interact_dist = 90
        self.show_hint = False
        self.current_obj = None

        self.tutorial_done = False
        self.chest_opened = False
        self.entered_zone = False
        self.enemy_defeated = False

        self.pending_action = None

        self.zone_timer = 2.5

        self.npc = pygame.Rect(700, 1600, 40, 50)
        self.chest = pygame.Rect(1400, 1100, 50, 40)
        self.enemy = pygame.Rect(2400, 1000, 50, 60)

        self.explore_zone = pygame.Rect(2100, 700, 700, 800)

        self.walls = [
            pygame.Rect(0, 0, self.world_width, 50),
            pygame.Rect(0, self.world_height - 50, self.world_width, 50),
            pygame.Rect(0, 0, 50, self.world_height),
            pygame.Rect(self.world_width - 50, 0, 50, self.world_height),
        ]

    def on_resize(self, new_w, new_h):
        self.width = new_w
        self.height = new_h
        self.dialogue.on_resize(new_w, new_h)

        max_cam_x = max(0, self.world_width - self.width)
        max_cam_y = max(0, self.world_height - self.height)
        self.cam_x = max(0, min(self.cam_x, max_cam_x))
        self.cam_y = max(0, min(self.cam_y, max_cam_y))

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
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self.execute_pause_option()
                return None

            if event.key == pygame.K_e:
                if self.dialogue.active:
                    self.dialogue.advance()

                    if not self.dialogue.active and self.pending_action:
                        action = self.pending_action
                        self.pending_action = None
                        return action

                    return None

                if self.current_obj:
                    return self.interact(self.current_obj)

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
            return None

        if self.pending_action and not self.dialogue.active:
            action = self.pending_action
            self.pending_action = None
            return action

        if self.zone_timer > 0:
            self.zone_timer -= dt
            if self.zone_timer < 0:
                self.zone_timer = 0

        if not self.dialogue.active:
            self.move(dt)
            self.check_events()

        self.update_camera()
        self.check_interaction()

        return None

    def draw_pause(self, screen):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("arial", 28)

        for i, option in enumerate(self.pause_options):
            color = (255, 255, 255) if i == self.pause_selected else (150, 150, 150)
            text = font.render(option, True, color)
            screen.blit(text, (self.width // 2 - 120, 220 + i * 60))

    def draw(self, screen):
        screen.fill((70, 120, 70))

        pygame.draw.rect(
            screen,
            (150, 120, 90),
            self.to_screen(pygame.Rect(200, 1500, 800, 300))
        )

        pygame.draw.rect(
            screen,
            (160, 160, 160),
            self.to_screen(pygame.Rect(1200, 900, 900, 700))
        )

        pygame.draw.rect(screen, (60, 100, 60), self.to_screen(self.explore_zone))
        pygame.draw.rect(screen, (255, 200, 80), self.to_screen(self.npc))

        if self.chest_opened:
            pygame.draw.rect(screen, (120, 80, 40), self.to_screen(self.chest))
        else:
            pygame.draw.rect(screen, (200, 150, 60), self.to_screen(self.chest))

        if not self.enemy_defeated:
            pygame.draw.rect(screen, (200, 60, 60), self.to_screen(self.enemy))

        pygame.draw.rect(screen, (60, 120, 255), self.to_screen(self.player))

        self.draw_ui(screen)
        self.dialogue.draw(screen)

        if self.paused:
            self.draw_pause(screen)

    def move(self, dt):
        keys = pygame.key.get_pressed()
        speed = self.run_speed if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.speed

        dx = 0.0
        dy = 0.0

        if keys[pygame.K_w]:
            dy -= speed * dt
            self.direction = "up"
        if keys[pygame.K_s]:
            dy += speed * dt
            self.direction = "down"
        if keys[pygame.K_a]:
            dx -= speed * dt
            self.direction = "left"
        if keys[pygame.K_d]:
            dx += speed * dt
            self.direction = "right"

        self.move_axis(dx, 0)
        self.move_axis(0, dy)

    def move_axis(self, dx, dy):
        if dx != 0:
            self.player_fx += dx
            self.player.x = int(round(self.player_fx))

            for w in self.get_collision_objects():
                if self.player.colliderect(w):
                    if dx > 0:
                        self.player.right = w.left
                    elif dx < 0:
                        self.player.left = w.right
                    self.player_fx = float(self.player.x)

        if dy != 0:
            self.player_fy += dy
            self.player.y = int(round(self.player_fy))

            for w in self.get_collision_objects():
                if self.player.colliderect(w):
                    if dy > 0:
                        self.player.bottom = w.top
                    elif dy < 0:
                        self.player.top = w.bottom
                    self.player_fy = float(self.player.y)

    def get_collision_objects(self):
        objs = self.walls + [self.npc]

        if not self.enemy_defeated:
            objs.append(self.enemy)

        return objs

    def update_camera(self):
        max_cam_x = max(0, self.world_width - self.width)
        max_cam_y = max(0, self.world_height - self.height)

        self.cam_x = max(0, min(self.player.centerx - self.width // 2, max_cam_x))
        self.cam_y = max(0, min(self.player.centery - self.height // 2, max_cam_y))

    def to_screen(self, rect):
        return pygame.Rect(
            rect.x - self.cam_x,
            rect.y - self.cam_y,
            rect.width,
            rect.height
        )

    def check_interaction(self):
        self.show_hint = False
        self.current_obj = None

        objs = [
            ("npc", self.npc),
            ("chest", self.chest),
            ("enemy", self.enemy)
        ]

        px, py = self.player.center
        best_name = None
        best_dist = None

        for name, obj in objs:
            if name == "chest" and self.chest_opened:
                continue
            if name == "enemy" and self.enemy_defeated:
                continue

            ox, oy = obj.center
            dist = ((px - ox) ** 2 + (py - oy) ** 2) ** 0.5

            if dist <= self.interact_dist:
                if best_name is None:
                    best_name = name
                    best_dist = dist
                else:
                    priority_current = self.get_interaction_priority(name)
                    priority_best = self.get_interaction_priority(best_name)

                    if priority_current < priority_best:
                        best_name = name
                        best_dist = dist
                    elif priority_current == priority_best and dist < best_dist:
                        best_name = name
                        best_dist = dist

        if best_name is not None:
            self.show_hint = True
            self.current_obj = best_name

    def get_interaction_priority(self, name):
        priorities = {
            "npc": 0,
            "chest": 1,
            "enemy": 2
        }
        return priorities.get(name, 999)

    def interact(self, obj):
        if obj == "npc":
            self.tutorial_done = True
            self.dialogue.start("Guía", [
                "Explora el mapa y descubre nuevas zonas.",
                "Abre cofres para conseguir objetos útiles.",
                "Enfrenta enemigos cuando estés preparado."
            ])
            return None

        elif obj == "chest":
            if self.chest_opened:
                return None

            self.chest_opened = True
            self.dialogue.start("Cofre", [
                "Obtienes 3 ciberballs.",
                "Podrás usarlas más adelante."
            ])
            return None

        elif obj == "enemy":
            if self.enemy_defeated:
                return None

            if not self.chest_opened:
                self.dialogue.start("Enemigo", [
                    "No estás listo aún.",
                    "Busca recursos primero."
                ])
                return None
            else:
                self.dialogue.start("Enemigo", [
                    "Prepárate...",
                    "¡Empieza el combate!"
                ])
                self.enemy_defeated = True
                self.pending_action = {"action": "start_battle"}
                return None

        return None

    def check_events(self):
        if self.player.colliderect(self.explore_zone) and not self.entered_zone:
            self.entered_zone = True
            self.dialogue.start("Sistema", [
                "Entraste a la zona de exploración.",
                "Aquí encontrarás desafíos y recompensas."
            ])

    def draw_ui(self, screen):
        font = pygame.font.SysFont("arial", 20)

        if self.zone_timer > 0:
            txt = font.render("Puerto Principal", True, (255, 255, 255))
            screen.blit(txt, (self.width // 2 - 80, 20))

        if self.show_hint and not self.dialogue.active and not self.paused:
            txt = font.render("Presiona E", True, (255, 255, 255))
            screen.blit(txt, (20, self.height - 40))

        obj = self.get_objective()
        txt = font.render("Objetivo: " + obj, True, (255, 255, 255))
        screen.blit(txt, (20, 20))

    def get_objective(self):
        if not self.tutorial_done:
            return "Habla con el guía"
        if not self.chest_opened:
            return "Abre el cofre"
        if not self.entered_zone:
            return "Explora"
        if not self.enemy_defeated:
            return "Derrota enemigo"
        return "Continúa..."

    def get_save_data(self):
        return {
            "scene": "virtual_world",
            "player": (self.player.x, self.player.y),
            "chest": self.chest_opened,
            "enemy": self.enemy_defeated,
            "zone": self.entered_zone,
            "tutorial": self.tutorial_done
        }

    def load_save_data(self, data):
        if not data:
            return

        self.player.x, self.player.y = data.get("player", (400, 1700))
        self.player_fx = float(self.player.x)
        self.player_fy = float(self.player.y)

        self.chest_opened = data.get("chest", False)
        self.enemy_defeated = data.get("enemy", False)
        self.entered_zone = data.get("zone", False)
        self.tutorial_done = data.get("tutorial", False)

        self.show_hint = False
        self.current_obj = None
        self.pending_action = None
        self.paused = False
        self.pause_selected = 0

        self.dialogue.active = False
        self.dialogue.lines = []
        self.dialogue.index = 0

        self.update_camera()


overworld = OverworldScene