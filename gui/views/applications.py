import threading

import customtkinter as ctk

from gui.views.base import BaseView
from launcher.exec import setup_and_launch
from launcher.time_keep import validate_whitelisted_days
from lib.config import read_json


def flatten_config(config, all_programs, prefix=""):
    for entry in config:
        item = config[entry]
        if isinstance(item, dict) and "script" not in item:
            flatten_config(item, all_programs, prefix + entry + " > ")
        else:
            display = prefix + entry
            item = dict(item)
            item["name"] = entry
            item["display_name"] = display
            all_programs.append(item)
    return all_programs


def load_programs():
    config = read_json("./config.json")
    programs = []
    if config:
        flatten_config(config, programs)
    return programs


class ApplicationsView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Applications")
        self.programs = []

        ctk.CTkLabel(
            self.body, text="Select an application and press Launch.",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=10, pady=(0, 8))

        self.status_label = ctk.CTkLabel(self.body, text="", text_color="#4CAF50")
        self.status_label.pack(anchor="w", padx=10)

        refresh_btn = ctk.CTkButton(self.body, text="Refresh List", command=self.refresh)
        refresh_btn.pack(anchor="w", padx=10, pady=(0, 8))

        self.listbox = ctk.CTkScrollableFrame(self.body, height=320)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.launch_btn = ctk.CTkButton(
            self.body, text="Launch", command=self._on_launch
        )
        self.launch_btn.pack(anchor="w", padx=10, pady=4)

        self.selected_name = None
        self.refresh()

    def refresh(self):
        self.programs = load_programs()
        for child in self.listbox.winfo_children():
            child.destroy()

        if not self.programs:
            ctk.CTkLabel(
                self.listbox, text="No applications found. Generate config.json first."
            ).pack(anchor="w", padx=4, pady=4)
            self.selected_name = None
            return

        self.selected_name = None
        for program in self.programs:
            btn = ctk.CTkButton(
                self.listbox,
                text=program["display_name"],
                anchor="w",
                fg_color="transparent",
                hover_color="gray20",
                command=lambda p=program: self._select(p),
            )
            btn.pack(fill="x", padx=2, pady=1)

    def _select(self, program):
        self.selected_name = program["name"]
        self.status_label.configure(text="Selected: " + program["display_name"])

    def _on_launch(self):
        if self.selected_name is None:
            self.status_label.configure(
                text="Select an application first.", text_color="#E53935"
            )
            return
        program = next(
            (p for p in self.programs if p["name"] == self.selected_name), None
        )
        if program is None:
            return
        self.launch_btn.configure(state="disabled")
        self.status_label.configure(
            text="Launching " + program["display_name"] + "...", text_color="#4CAF50"
        )
        threading.Thread(target=self._launch_worker, args=(program,), daemon=True).start()

    def _launch_worker(self, program):
        try:
            is_logging_time = bool(program.get("time_limit", False))
            if is_logging_time:
                validate_whitelisted_days()
            setup_and_launch(is_logging_time, program)
            msg = "Launched " + program["display_name"]
        except Exception as exc:
            msg = "Launch failed: " + str(exc)

        def update():
            self.launch_btn.configure(state="normal")
            self.status_label.configure(
                text=msg, text_color="#E53935" if msg.startswith("Launch failed") else "#4CAF50"
            )

        self.after(0, update)
