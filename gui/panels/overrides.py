from config_lib.overrides import OverridesConfig

from gui.panels.base import BasePanel


class OverridesPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Overrides")
        self.is_client = is_client

    def _build(self):
        config = OverridesConfig(self.is_client)
        editor = self.add_json_editor(config.fetch_overrides())

        def save():
            config.update_overrides(editor.get())
            self.set_status("Saved overrides config")

        self.add_save_button(save)
