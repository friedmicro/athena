"""Steam host & scanning configuration."""
import customtkinter as ctk

from config_lib.steam import SteamConfig

from gui.panels.base import BasePanel
from gui.widgets import JsonEditor, labeled_entry, section_label

NON_HOST_KEYS = ("remapping", "exclude")


class SteamPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Steam")
        self.is_client = is_client

    def _build(self):
        config = SteamConfig(self.is_client)
        hosts = [k for k in config.config_data.keys() if k not in NON_HOST_KEYS]

        section_label(self.body, "Host")
        self.host_menu = ctk.CTkOptionMenu(self.body, values=hosts, command=self._on_select_host)
        self.host_menu.pack(fill="x", pady=4)
        self.host_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.host_container.pack(fill="both", expand=True, pady=4)

        section_label(self.body, "Remapping")
        remapping_editor = self.add_json_editor(config.fetch_remapping())

        section_label(self.body, "Exclude")
        exclude_editor = self.add_json_editor(config.fetch_exclude())

        def save():
            config.update_remapping(remapping_editor.get())
            config.update_exclude(exclude_editor.get())
            self.set_status("Saved steam config")

        self.config = config
        self.remapping_editor = remapping_editor
        self.exclude_editor = exclude_editor
        self.selected_host = hosts[0] if hosts else None
        if self.selected_host is not None:
            self._render_host()

        self.add_save_button(save)

    def _on_select_host(self, host):
        self.selected_host = host
        self._render_host()

    def _render_host(self):
        for child in self.host_container.winfo_children():
            child.destroy()

        if self.selected_host is None:
            return

        host = self.config.fetch_host(self.selected_host)
        os_var = labeled_entry(self.host_container, "OS", host.get("os", ""))
        native_var = labeled_entry(self.host_container, "Native", host.get("native", ""))
        flatpak_var = labeled_entry(self.host_container, "Flatpak", host.get("flatpak", ""))

        section_label(self.host_container, "Locations")
        locations_editor = JsonEditor(self.host_container, host.get("locations", []))
        locations_editor.pack(fill="both", expand=True)

        def save_host():
            new_host = {
                "os": os_var.get(),
                "native": native_var.get(),
                "flatpak": flatpak_var.get(),
                "locations": locations_editor.get(),
            }
            self.config.update_host(self.selected_host, new_host)
            self.set_status("Saved steam host")

        ctk.CTkButton(self.host_container, text="Save Host", command=save_host).pack(anchor="w", pady=6)
