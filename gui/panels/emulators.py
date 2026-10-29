"""Emulator configuration."""
import customtkinter as ctk

from config_lib.emulators import EmulatorConfig
from gui.panels.base import BasePanel
from gui.widgets import JsonEditor, labeled_entry, labeled_switch, section_label

EMULATOR_FIELDS = [
    ("paths", "str"),
    ("scan", "bool"),
    ("extensions", "list"),
    ("is_single_file", "bool"),
    ("truncate_sequence", "str"),
    ("exec", "str"),
]


class EmulatorsPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Emulators")
        self.is_client = is_client

    def _build(self):
        self.config = EmulatorConfig(self.is_client)
        emulators = sorted(self.config.fetch_emulators().keys())

        # Name entry for adding a new emulator.
        add_row = ctk.CTkFrame(self.body, fg_color="transparent")
        add_row.pack(fill="x", pady=4)
        self.new_name_var = ctk.StringVar(value="")
        ctk.CTkLabel(add_row, text="New emulator", width=140, anchor="w").pack(side="left")
        ctk.CTkEntry(add_row, textvariable=self.new_name_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ctk.CTkButton(add_row, text="Add", width=70, command=self._add_emulator).pack(
            side="left"
        )

        section_label(self.body, "Emulator")
        self.host_menu = ctk.CTkOptionMenu(
            self.body, values=emulators, command=self._on_select_emulator
        )
        self.host_menu.pack(fill="x", pady=4)
        self.detail_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.detail_container.pack(fill="both", expand=True, pady=4)

        section_label(self.body, "Remapping")
        self.remapping_editor = self.add_json_editor(self.config.fetch_remapping())

        section_label(self.body, "Selected")
        self.selected_editor = self.add_json_editor(self.config.fetch_selected())

        def save():
            self.config.update_remapping(self.remapping_editor.get())
            self.config.update_selected(self.selected_editor.get())
            self.set_status("Saved emulator config")

        self.selected_emulator = emulators[0] if emulators else None
        if self.selected_emulator is not None:
            self._render_emulator()

        self.add_save_button(save)

    # ------------------------------------------------------------------

    def _add_emulator(self):
        name = self.new_name_var.get().strip()
        if not name:
            return
        self.config.add_emulator(name)
        values = sorted(self.config.fetch_emulators().keys())
        self.host_menu.configure(values=values)
        if name in values:
            self.host_menu.set(name)
        self.new_name_var.set("")
        self._on_select_emulator(name)
        self.set_status("Added emulator")

    def _on_select_emulator(self, name):
        self.selected_emulator = name
        self._render_emulator()

    def _render_emulator(self):
        for child in self.detail_container.winfo_children():
            child.destroy()

        if self.selected_emulator is None:
            return

        emulator = self.config.fetch_emulator(self.selected_emulator)
        widgets = {}
        for field, field_type in EMULATOR_FIELDS:
            value = emulator.get(field, "")
            if field_type == "bool":
                widgets[field] = labeled_switch(self.detail_container, field, value)
            elif field_type == "list":
                widgets[field] = JsonEditor(self.detail_container, value)
                widgets[field].pack(fill="both", expand=True)
            else:
                widgets[field] = labeled_entry(self.detail_container, field, value)

        def save_emulator():
            new = {field: widgets[field].get() for field, _ in EMULATOR_FIELDS}
            self.config.update_emulator(self.selected_emulator, new)
            self.set_status("Saved emulator")

        ctk.CTkButton(
            self.detail_container, text="Save Emulator", command=save_emulator
        ).pack(anchor="w", pady=6)