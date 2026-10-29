import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    def __init__(self, master, title=""):
        super().__init__(master, fg_color="transparent")
        self.view_title = title

        header = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 6))

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)
