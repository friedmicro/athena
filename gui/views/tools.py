import os
import subprocess
import sys
import threading

import customtkinter as ctk

from config_lib.client import GeneratorConfig
from gui.views.base import BaseView


class ToolsView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Tools")

        self.status_label = ctk.CTkLabel(self.body, text="", text_color="#4CAF50")
        self.status_label.pack(anchor="w", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            self.body,
            text="Regenerate the generated config (config.json) from your "
            "source configuration files.",
            font=ctk.CTkFont(size=14),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 8))

        self.generate_btn = ctk.CTkButton(
            self.body, text="Generate config.json", command=self._on_generate
        )
        self.generate_btn.pack(anchor="w", padx=10, pady=4)

    def _on_generate(self):
        self.generate_btn.configure(state="disabled")
        self.status_label.configure(
            text="Generating config.json...", text_color="#4CAF50"
        )
        threading.Thread(target=self._generate_worker, daemon=True).start()

    def _generator_command(self):
        """Return the command to run to generate the config.

        Prefer the configured generator binary; fall back to running
        ``generator.py`` directly when the binary hasn't been built yet.
        """
        try:
            generator_config = GeneratorConfig()
            binary = generator_config.generator_path
        except Exception:  # noqa: BLE001
            binary = None

        if binary and os.path.exists(binary):
            return [binary]

        if os.path.exists("./generator.py"):
            return [sys.executable, "generator.py"]

        return None

    def _generate_worker(self):
        command = self._generator_command()
        if command is None:
            msg = "No generator found (configured binary and ./generator.py missing)."
        else:
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, cwd=".", check=False
                )
                if result.returncode == 0:
                    msg = "config.json generated successfully."
                else:
                    detail = result.stderr.strip() or result.stdout.strip()
                    msg = "Generation failed: " + (detail or "unknown error")
            except Exception as exc:  # noqa: BLE001
                msg = "Generation error: " + str(exc)

        def update():
            self.generate_btn.configure(state="normal")
            self.status_label.configure(
                text=msg,
                text_color="#E53935" if "fail" in msg.lower() or "error" in msg.lower() else "#4CAF50",
            )

        self.after(0, update)
