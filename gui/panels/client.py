from config_lib.client import ClientConfig, GeneratorConfig

from gui.panels.base import BasePanel
from gui.widgets import labeled_entry, labeled_switch, section_label

GENERATOR_FIELDS = [
    ("keep_temp", "bool"),
    ("scanner_enabled", "bool"),
    ("partials_enabled", "bool"),
    ("generator_path", "str"),
    ("python", "str"),
    ("node", "str"),
]


class ClientPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Client")
        self.is_client = is_client

    def _build(self):
        client = ClientConfig()

        section_label(self.body, "Machine")
        machine_id = labeled_entry(self.body, "Machine ID", client.fetch_id())

        section_label(self.body, "Generator")
        generator = GeneratorConfig()
        widgets = {}
        for field, field_type in GENERATOR_FIELDS:
            if field_type == "bool":
                widgets[field] = labeled_switch(self.body, field, generator[field])
            else:
                widgets[field] = labeled_entry(self.body, field, generator[field])

        def save():
            client.update_id(machine_id.get())
            new_generator = GeneratorConfig()
            for field, field_type in GENERATOR_FIELDS:
                new_generator[field] = widgets[field].get()
            client.update_generator(new_generator)
            self.set_status("Saved client config")

        self.add_save_button(save)
