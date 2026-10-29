"""Main application window for the Athena desktop GUI."""
import customtkinter as ctk

from gui.views.applications import ApplicationsView
from gui.views.settings import SettingsView
from gui.views.tools import ToolsView

NAV_ITEMS = [
    ("Applications", ApplicationsView),
    ("Tools", ToolsView),
    ("Settings", SettingsView),
]


class AthenaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Athena")
        self.geometry("1000x680")
        self.minsize(820, 560)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.nav_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.nav_frame, text="Athena", font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=16, pady=(20, 16))

        self.nav_buttons = {}
        for label, _view_class in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=label,
                anchor="w",
                command=lambda l=label: self.show_view(l),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[label] = btn

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.views = {}
        self.current_view = None
        self.show_view("Applications")

    def show_view(self, label):
        view = self.views.get(label)
        if view is None:
            view_class = {l: c for l, c in NAV_ITEMS}[label]
            view = view_class(self.content_frame)
            self.views[label] = view

        for _label, btn in self.nav_buttons.items():
            if _label == label:
                btn.configure(fg_color="gray25")
            else:
                btn.configure(fg_color="transparent")

        if self.current_view is not None:
            self.current_view.pack_forget()
        view.pack(fill="both", expand=True)
        self.current_view = view
