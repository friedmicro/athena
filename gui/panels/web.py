from config_lib.web import WebConfig

from gui.panels.base import BasePanel
from gui.widgets import labeled_entry, labeled_switch, section_label


class WebPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Web")
        self.is_client = is_client

    def _build(self):
        config = WebConfig(self.is_client)

        section_label(self.body, "Browser")
        browser = labeled_entry(self.body, "Browser", config.fetch_browser())
        close_existing = labeled_switch(self.body, "Close existing", config.fetch_close_existing())
        kiosk = labeled_switch(self.body, "Kiosk mode", config.fetch_kiosk())
        check_ip = labeled_entry(self.body, "Check IP", config.fetch_check_ip())

        section_label(self.body, "Games")
        editor = self.add_json_editor(config.fetch_programs())

        def save():
            config.update_browser(browser.get())
            config.update_close_existing(close_existing.get())
            config.update_kiosk(kiosk.get())
            config.update_check_ip(check_ip.get())
            config.update_config(editor.get())
            self.set_status("Saved web config")

        self.add_save_button(save)
