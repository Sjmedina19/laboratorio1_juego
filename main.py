import pygame
import sys
import os
import json

from scenes.menu import MenuScene
from scenes.world import WorldScene
from scenes.settings import SettingsScene
from scenes.loading import LoadingScene
from scenes.overworld import OverworldScene

pygame.init()

FPS = 60
SAVE_PATH = os.path.join("saves", "slot1.json")

class Game:
    def __init__(self):
        self.running = True
        self.available_resolutions = [
            (1280, 720), (1366, 768), (1600, 900), (1920, 1080)
        ]
        self.settings = {
            "music_volume": 80,
            "sfx_volume": 80,
            "mute_music": False,
            "mute_sfx": False,
            "fullscreen": False,
            "resolution_index": 0
        }
        self.clock = pygame.time.Clock()
        self.screen = None
        self.previous_scene_type = "menu"
        self.previous_world_save = None
        self.sfx = {}
        self.music = None

        self.apply_display_settings()
        self.load_audio()

        self.current_scene = MenuScene(self, self.screen.get_width(), self.screen.get_height())

    def apply_display_settings(self):
        if self.settings["fullscreen"]:
            info = pygame.display.Info()
            width, height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            width, height = self.available_resolutions[self.settings["resolution_index"]]
            self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Laboratorio 1 - Juego")
        if hasattr(self, "current_scene") and hasattr(self.current_scene, "on_resize"):
            self.current_scene.on_resize(self.screen.get_width(), self.screen.get_height())

    def load_audio(self):
        click_path = os.path.join("assets","sounds","click.wav")
        if os.path.exists(click_path):
            self.sfx["click"] = pygame.mixer.Sound(click_path)
        music_path = os.path.join("assets","sounds","musica1.mp3")
        if os.path.exists(music_path):
            self.music = pygame.mixer.Sound(music_path)
            self.music.set_volume(self.settings["music_volume"]/100)
            self.music.play(-1)

    def save_game(self, save_data):
        os.makedirs("saves", exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4)

    def load_game(self):
        if not os.path.exists(SAVE_PATH):
            return None
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def start_new_game(self):
        self.current_scene = WorldScene(self.screen.get_width(), self.screen.get_height())

    def continue_game(self):
        save_data = self.load_game()
        if save_data is None:
            self.current_scene = MenuScene(self, self.screen.get_width(), self.screen.get_height(), message="No hay partida guardada.")
            return
        scene_name = save_data.get("scene", "bedroom")
        if scene_name == "virtual_world":
            world = OverworldScene(self.screen.get_width(), self.screen.get_height())
        else:
            world = WorldScene(self.screen.get_width(), self.screen.get_height())
        world.load_save_data(save_data)
        self.current_scene = world

    def open_settings(self):
        if isinstance(self.current_scene, (WorldScene, OverworldScene)):
            self.previous_scene_type = "game"
            self.previous_world_save = self.current_scene.get_save_data()
        else:
            self.previous_scene_type = "menu"
            self.previous_world_save = None
        self.current_scene = SettingsScene(
            self.screen.get_width(), self.screen.get_height(), self.settings, self.available_resolutions
        )

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            scene_result = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                result = self.current_scene.handle_event(event)
                if result:
                    action = result.get("action")
                    if action == "new_game":
                        self.start_new_game()
                    elif action == "continue_game":
                        self.continue_game()
                    elif action == "settings":
                        self.open_settings()
                    elif action == "quit":
                        self.running = False
            if self.running:
                self.current_scene.update(dt)
                self.current_scene.draw(self.screen)
                pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()