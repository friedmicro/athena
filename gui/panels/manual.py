from config_lib.manual import ManualConfig

from gui.panels.base import BasePanel


class ManualPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Manual")
        self.is_client = is_client

    def _build(self):
        config = ManualConfig(self.is_client)
        editor = self.add_json_editor(config.fetch_data())

        def save():
            config.raw_data = editor.get()
            config.write_to_file()
            self.set_status("Saved manual config")

        self.add_save_button(save)
