import customtkinter as ctk

from gui.widgets import JsonEditor, save_button


class BasePanel(ctk.CTkScrollableFrame):
    def __init__(self, master, title=""):
        super().__init__(master, fg_color="transparent")
        self.panel_title = title

        header = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(anchor="w", padx=10, pady=(10, 2))

        self.status_label = ctk.CTkLabel(self, text="", text_color="#4CAF50")
        self.status_label.pack(anchor="w", padx=10)

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)

    def load(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.set_status("")
        self._build()

    def _build(self):
        raise NotImplementedError

    def set_status(self, text, ok=True):
        self.status_label.configure(
            text=text, text_color="#4CAF50" if ok else "#E53935"
        )

    def add_json_editor(self, value):
        editor = JsonEditor(self.body, value)
        editor.pack(fill="both", expand=True)
        return editor

    def add_save_button(self, command, text="Save"):
        return save_button(self.body, text=text, command=command)
