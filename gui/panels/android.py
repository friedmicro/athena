from config_lib.android import AndroidConfig

from gui.panels.base import BasePanel


class AndroidPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Android (Waydroid)")
        self.is_client = is_client

    def _build(self):
        config = AndroidConfig(self.is_client)
        editor = self.add_json_editor(config.load_apps())

        def save():
            config.update_config(editor.get())
            self.set_status("Saved Android config")

        self.add_save_button(save)
