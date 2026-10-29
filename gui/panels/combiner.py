import customtkinter as ctk

from config_lib.combiner import CombinerConfig

from gui.panels.base import BasePanel
from gui.widgets import JsonEditor, labeled_entry, section_label


class CombinerPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Combiner")
        self.is_client = is_client

    def _build(self):
        config = CombinerConfig(self.is_client)
        files = config.fetch_files()

        section_label(self.body, "Combiner Files")

        self.file_menu = ctk.CTkOptionMenu(
            self.body, values=files, command=self._on_select_file
        )
        self.file_menu.pack(fill="x", pady=4)

        new_row = ctk.CTkFrame(self.body, fg_color="transparent")
        new_row.pack(fill="x", pady=4)
        self.new_file_var = ctk.StringVar(value="")
        new_entry = ctk.CTkEntry(new_row, textvariable=self.new_file_var, placeholder_text="New combiner file name")
        new_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(new_row, text="Add", width=60, command=self._add_file).pack(side="right")

        self.form_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, pady=6)

        self.config = config
        self.selected_file = files[0] if files else None
        if self.selected_file is not None:
            self._render_form()

    # ------------------------------------------------------------------

    def _add_file(self):
        name = self.new_file_var.get().strip()
        if not name:
            return
        self.config.add_combiner_file(name)
        self.set_status("Added combiner file")
        self.load()

    def _on_select_file(self, file_name):
        self.selected_file = file_name
        self._render_form()

    def _render_form(self):
        for child in self.form_container.winfo_children():
            child.destroy()

        if self.selected_file is None:
            ctk.CTkLabel(self.form_container, text="No combiner files defined.").pack(anchor="w")
            return

        editor = JsonEditor(self.form_container, self.config.file_data[self.selected_file])
        editor.pack(fill="both", expand=True)

        def save():
            self.config.file_data[self.selected_file] = editor.get()
            self.config.write_config()
            self.set_status("Saved combiner file")

        ctk.CTkButton(self.form_container, text="Save", command=save).pack(anchor="w", pady=6)
