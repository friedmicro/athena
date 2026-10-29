from config_lib.accessibility import AccessibilityConfig

from gui.panels.base import BasePanel
from gui.widgets import labeled_entry, labeled_switch, section_label


class AccessibilityPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Accessibility")
        self.is_client = is_client

    def _build(self):
        config = AccessibilityConfig(self.is_client)
        data = config.config_data

        section_label(self.body, "General")
        generate = labeled_switch(
            self.body, "Generate config", data.get("generate_config", False)
        )

        section_label(self.body, "Whitelisted Entries")
        entries = labeled_entry(
            self.body, "Whitelisted entries",
            ", ".join(data.get("whitelisted_entries", [])),
        )

        def save():
            new_data = dict(data)
            new_data["generate_config"] = generate.get()
            new_data["whitelisted_entries"] = [
                item.strip() for item in entries.get().split(",") if item.strip()
            ]
            config.write_config(new_data)
            self.set_status("Saved accessibility config")

        self.add_save_button(save)
