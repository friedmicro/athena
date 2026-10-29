import json
import os

import customtkinter as ctk

from gui.panels import CONFIG_PANELS
from gui.views.base import BaseView
from gui.widgets import (
    JsonEditor,
    client_directory,
    list_client_ids,
    read_client_file,
    write_client_file,
)

CONFIG_DIR = "./config"
CONFIG_JSON_PATH = "./config.json"
EXPOSED_CONFIG_FILES = [
    "accessibility.json",
    "android.json",
    "client.json",
    "combiner.json",
    "emulators.json",
    "local.json",
    "manual.json",
    "overrides.json",
    "remote.json",
    "steam.json",
    "time_config.json",
    "web.json",
    "windows_games.json",
]


class SettingsView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Settings")

        self.targets = ["Base Config"] + list_client_ids()
        self.current_target = "Base Config"
        self.current_category = None
        self.current_client_file = None

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(toolbar, text="Target:").pack(side="left", padx=(0, 6))
        self.target_menu = ctk.CTkOptionMenu(
            toolbar, values=self.targets, command=self._on_target_change
        )
        self.target_menu.pack(side="left", padx=(0, 10))

        self.view_config_btn = ctk.CTkButton(
            toolbar, text="View config.json", command=self._view_config_json
        )
        self.view_config_btn.pack(side="left", padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            toolbar, text="Copy to Client...", command=self._copy_to_client
        )
        self.copy_btn.pack(side="left")

        self.toolbar_status = ctk.CTkLabel(toolbar, text="", text_color="#4CAF50")
        self.toolbar_status.pack(side="left", padx=10)

        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkScrollableFrame(split, width=200, fg_color="transparent")
        self.sidebar.pack(side="left", fill="y", padx=(0, 8))

        self.content = ctk.CTkFrame(split, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True)

        self._render_sidebar()

    def _render_sidebar(self):
        for child in self.sidebar.winfo_children():
            child.destroy()

        if self.current_target == "Base Config":
            self._render_category_sidebar()
        else:
            self._render_client_file_sidebar()

    def _render_category_sidebar(self):
        for label, _panel_class in CONFIG_PANELS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="gray20",
                command=lambda l=label: self._on_category_select(l),
            )
            btn.pack(fill="x", padx=2, pady=1)

    def _render_client_file_sidebar(self):
        files = read_client_files(self.current_target)
        if not files:
            ctk.CTkLabel(
                self.sidebar, text="No config files for this client."
            ).pack(anchor="w", padx=4, pady=4)
            return
        for filename in files:
            btn = ctk.CTkButton(
                self.sidebar,
                text=filename,
                anchor="w",
                fg_color="transparent",
                hover_color="gray20",
                command=lambda f=filename: self._on_client_file_select(f),
            )
            btn.pack(fill="x", padx=2, pady=1)

    def _render_content(self):
        for child in self.content.winfo_children():
            child.destroy()

        if self.current_target == "Base Config":
            self._render_category_content()
        else:
            self._render_client_file_content()

    def _render_category_content(self):
        if self.current_category is None:
            ctk.CTkLabel(
                self.content, text="Select a configuration category on the left."
            ).pack(anchor="w", padx=10, pady=10)
            return
        panel_class = dict(CONFIG_PANELS).get(self.current_category)
        if panel_class is None:
            return
        panel = panel_class(self.content)
        panel.pack(fill="both", expand=True)
        panel.load()

    def _render_client_file_content(self):
        if self.current_client_file is None:
            ctk.CTkLabel(
                self.content, text="Select a config file on the left."
            ).pack(anchor="w", padx=10, pady=10)
            return
        client_id = self.current_target
        filename = self.current_client_file
        data = read_client_file(client_id, filename)
        editor = JsonEditor(self.content, data)
        editor.pack(fill="both", expand=True)

        def save():
            write_client_file(client_id, filename, editor.get())
            self._set_toolbar_status("Saved " + filename + " for " + client_id)

        ctk.CTkButton(self.content, text="Save", command=save).pack(
            anchor="w", padx=10, pady=6
        )

    def _on_target_change(self, target):
        self.current_target = target
        self.current_category = None
        self.current_client_file = None
        self._render_sidebar()
        self._render_content()

    def _on_category_select(self, label):
        self.current_category = label
        self._render_content()

    def _on_client_file_select(self, filename):
        self.current_client_file = filename
        self._render_content()

    def _set_toolbar_status(self, text, ok=True):
        self.toolbar_status.configure(
            text=text, text_color="#4CAF50" if ok else "#E53935"
        )

    def _view_config_json(self):
        if not os.path.exists(CONFIG_JSON_PATH):
            self._set_toolbar_status("config.json not found", ok=False)
            return
        with open(CONFIG_JSON_PATH, "r") as handle:
            text = handle.read()

        dialog = ctk.CTkToplevel(self)
        dialog.title("config.json")
        dialog.geometry("720x560")
        dialog.grab_set()

        label = ctk.CTkLabel(dialog, text="Generated client config (config.json)")
        label.pack(padx=10, pady=(10, 4))

        textbox = ctk.CTkTextbox(dialog, wrap="none")
        textbox.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(
            anchor="e", padx=10, pady=(0, 10)
        )

    def _copy_to_client(self):
        """Copy a base config file into a client folder."""
        if self.current_target != "Base Config":
            self._set_toolbar_status("Switch Target to 'Base Config' to copy from it.", ok=False)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Copy Config to Client")
        dialog.geometry("420x240")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Config file:").pack(anchor="w", padx=12, pady=(10, 2))
        file_var = ctk.StringVar(value=EXPOSED_CONFIG_FILES[0])
        ctk.CTkOptionMenu(
            dialog, values=EXPOSED_CONFIG_FILES, variable=file_var
        ).pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(dialog, text="Target client:").pack(anchor="w", padx=12, pady=(0, 2))
        client_ids = list_client_ids()
        if not client_ids:
            ctk.CTkLabel(
                dialog, text="No client folders configured."
            ).pack(padx=12, pady=8)
            ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(
                anchor="e", padx=12, pady=(0, 10)
            )
            return
        client_var = ctk.StringVar(value=client_ids[0])
        ctk.CTkOptionMenu(dialog, values=client_ids, variable=client_var).pack(
            fill="x", padx=12, pady=(0, 12)
        )

        def do_copy():
            filename = file_var.get()
            client_id = client_var.get()
            source = os.path.join(CONFIG_DIR, filename)
            if not os.path.exists(source):
                self._set_toolbar_status("Source file not found: " + filename, ok=False)
                dialog.destroy()
                return
            data = read_json_file(source)
            write_client_file(client_id, filename, data)
            dialog.destroy()
            self._set_toolbar_status("Copied " + filename + " to " + client_id)
            self.targets = ["Base Config"] + list_client_ids()
            self.target_menu.configure(values=self.targets)

        ctk.CTkButton(dialog, text="Copy", command=do_copy).pack(
            anchor="e", padx=12, pady=(0, 10)
        )


def read_json_file(path):
    with open(path, "r") as handle:
        return json.load(handle)


def read_client_files(client_id):
    """Config files present in the given client's folder."""
    directory = client_directory(client_id)
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith(".json"))
