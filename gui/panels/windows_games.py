from config_lib.windows_games import WindowsGamesConfig

from gui.panels.base import BasePanel
from gui.widgets import labeled_entry, section_label


class WindowsGamesPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Windows Games")
        self.is_client = is_client

    def _build(self):
        config = WindowsGamesConfig(self.is_client)

        section_label(self.body, "Steam Path")
        steam_path = labeled_entry(self.body, "Steam path", config.fetch_steam_path())

        section_label(self.body, "Exclude")
        exclude_editor = self.add_json_editor(config.fetch_exclude())

        section_label(self.body, "Open Steam Direct")
        direct_editor = self.add_json_editor(config.fetch_open_steam_direct())

        def save():
            config.update_steam_path(steam_path.get())
            config.update_exclude(exclude_editor.get())
            config.update_open_steam_direct(direct_editor.get())
            self.set_status("Saved windows games config")

        self.add_save_button(save)
