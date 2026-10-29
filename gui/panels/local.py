from config_lib.local import LocalConfig

from gui.panels.base import BasePanel


class LocalPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Local")
        self.is_client = is_client

    def _build(self):
        config = LocalConfig(self.is_client)
        editor = self.add_json_editor(config.fetch_local())

        def save():
            config.update_local(editor.get())
            self.set_status("Saved local config")

        self.add_save_button(save)
