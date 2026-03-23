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
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080)
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
        self.current_music_path = None

        self.audio_available = self.init_audio()
        self.menu_music_path = self.find_menu_music_path()
        self.sfx_paths = self.find_sfx_paths()
        self.sfx = self.load_sfx()

        self.previous_scene_type = "menu"
        self.previous_world_save = None

        self.apply_display_settings()

        self.current_scene = MenuScene(
            self.screen.get_width(),
            self.screen.get_height()
        )
        self.update_music_for_scene()

    def init_audio(self):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def find_menu_music_path(self):
        candidates = [
            os.path.join("assets", "music", "delon_boomkin-tribal-drum-rhythm-463957.mp3"),
            os.path.join("assets", "music", "363_full_game-of-rings_0155_preview.mp3.mpeg"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def find_sfx_paths(self):
        return {
            "click": os.path.join("assets", "sounds", "click.wav.mp3"),
            "save": os.path.join("assets", "sounds", "recoger.wav.mp3"),
            "interact": os.path.join("assets", "sounds", "cofre.wav.mp3"),
            "error": os.path.join("assets", "sounds", "collision.wav.mp3"),
        }

    def load_sfx(self):
        if not self.audio_available:
            return {}

        loaded = {}
        for key, path in self.sfx_paths.items():
            if os.path.exists(path):
                try:
                    loaded[key] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass
        self.apply_audio_settings()
        return loaded

    def apply_audio_settings(self):
        if not self.audio_available:
            return

        music_volume = 0.0 if self.settings["mute_music"] else max(0.0, min(1.0, self.settings["music_volume"] / 100.0))
        sfx_volume = 0.0 if self.settings["mute_sfx"] else max(0.0, min(1.0, self.settings["sfx_volume"] / 100.0))

        pygame.mixer.music.set_volume(music_volume)
        for snd in self.sfx.values():
            snd.set_volume(sfx_volume)

    def play_sfx(self, name):
        if not self.audio_available:
            return
        snd = self.sfx.get(name)
        if snd is not None:
            snd.play()

    def update_music_for_scene(self):
        if not self.audio_available:
            return

        target_music = self.menu_music_path if isinstance(self.current_scene, MenuScene) else None
        if target_music is None:
            if self.current_music_path is not None:
                pygame.mixer.music.stop()
                self.current_music_path = None
            return

        if self.current_music_path != target_music:
            try:
                pygame.mixer.music.load(target_music)
                pygame.mixer.music.play(-1)
                self.current_music_path = target_music
            except pygame.error:
                self.current_music_path = None
                return

        self.apply_audio_settings()

    def apply_display_settings(self):
        if self.settings["fullscreen"]:
            info = pygame.display.Info()
            width, height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            width, height = self.available_resolutions[self.settings["resolution_index"]]
            self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption("Laboratorio 1 - Juego")

        # 🔥 FIX: evitar crash antes de crear escena
        if hasattr(self, "current_scene") and hasattr(self.current_scene, "on_resize"):
            self.current_scene.on_resize(
                self.screen.get_width(),
                self.screen.get_height()
            )

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
        self.current_scene = WorldScene(
            self.screen.get_width(),
            self.screen.get_height()
        )

    def continue_game(self):
        save_data = self.load_game()

        if save_data is None:
            self.current_scene = MenuScene(
                self.screen.get_width(),
                self.screen.get_height(),
                message="No hay partida guardada."
            )
            return

        scene_name = save_data.get("scene", "bedroom")

        if scene_name == "virtual_world":
            world = OverworldScene(
                self.screen.get_width(),
                self.screen.get_height()
            )
        else:
            world = WorldScene(
                self.screen.get_width(),
                self.screen.get_height()
            )

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
            self.screen.get_width(),
            self.screen.get_height(),
            self.settings,
            self.available_resolutions
        )

    def preview_settings(self, new_settings):
        self.settings = new_settings.copy()
        self.apply_display_settings()
        self.apply_audio_settings()

        self.current_scene = SettingsScene(
            self.screen.get_width(),
            self.screen.get_height(),
            self.settings,
            self.available_resolutions
        )
        self.update_music_for_scene()

    def close_settings(self, new_settings):
        self.settings = new_settings.copy()
        self.apply_display_settings()
        self.apply_audio_settings()

        if self.previous_scene_type == "game" and self.previous_world_save is not None:
            scene_name = self.previous_world_save.get("scene", "bedroom")

            if scene_name == "virtual_world":
                world = OverworldScene(
                    self.screen.get_width(),
                    self.screen.get_height()
                )
            else:
                world = WorldScene(
                    self.screen.get_width(),
                    self.screen.get_height()
                )

            world.load_save_data(self.previous_world_save)

            if hasattr(world, "on_resize"):
                world.on_resize(self.screen.get_width(), self.screen.get_height())

            if hasattr(world, "paused"):
                world.paused = True

            self.current_scene = world
        else:
            self.current_scene = MenuScene(
                self.screen.get_width(),
                self.screen.get_height()
            )
        self.update_music_for_scene()

    def return_to_menu(self, message=""):
        self.current_scene = MenuScene(
            self.screen.get_width(),
            self.screen.get_height(),
            message=message
        )
        self.update_music_for_scene()

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

                    if action == "play_sfx":
                        self.play_sfx(result.get("sfx", "click"))
                        continue

                    if action == "new_game":
                        self.play_sfx("click")
                        self.start_new_game()
                        self.update_music_for_scene()

                    elif action == "continue_game":
                        self.play_sfx("click")
                        self.continue_game()
                        self.update_music_for_scene()

                    elif action == "settings":
                        self.play_sfx("click")
                        self.open_settings()
                        self.update_music_for_scene()

                    elif action == "preview_settings":
                        self.preview_settings(result["settings"])

                    elif action == "back_from_settings":
                        self.play_sfx("click")
                        self.close_settings(result["settings"])

                    elif action == "start_loading_virtual_world":
                        self.play_sfx("interact")
                        self.current_scene = LoadingScene(
                            self.screen.get_width(),
                            self.screen.get_height(),
                            next_scene_factory=lambda: OverworldScene(
                                self.screen.get_width(),
                                self.screen.get_height()
                            ),
                            duration=1.5
                        )
                        self.update_music_for_scene()

                    elif action == "finish_loading":
                        self.current_scene = result["next_scene"]
                        self.update_music_for_scene()

                    elif action == "quit":
                        self.play_sfx("click")
                        self.running = False

                    elif action == "save_game":
                        self.play_sfx("save")
                        save_data = self.current_scene.get_save_data()
                        self.save_game(save_data)

                    elif action == "save_and_menu":
                        self.play_sfx("save")
                        save_data = self.current_scene.get_save_data()
                        self.save_game(save_data)
                        self.return_to_menu("Partida guardada.")

                    elif action == "menu_without_save":
                        self.play_sfx("click")
                        self.return_to_menu("Volviste al menú.")

            if self.running:
                update_result = self.current_scene.update(dt)
                if update_result:
                    scene_result = update_result

            if scene_result:
                if scene_result["action"] == "finish_loading":
                    self.current_scene = scene_result["next_scene"]
                    self.update_music_for_scene()

            self.current_scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()