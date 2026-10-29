import customtkinter as ctk

from config_lib.remote import RemoteConfig
from gui.panels.base import BasePanel
from gui.widgets import (
    JsonEditor,
    labeled_entry,
    labeled_selector,
    labeled_switch,
    section_label,
)

COMMON_FIELDS = [
    ("os", "str"),
    ("ip", "str"),
    ("live_check", "str"),
    ("remote_client_type", "selector"),
    ("start_script", "str"),
    ("stop_script", "str"),
    ("skip_assets", "bool"),
    ("athena_installed", "bool"),
    ("skip_stop_command", "bool"),
]

MOONLIGHT_FIELDS = [
    ("moonlight_app", "str"),
    ("moonlight_machine", "str"),
]
RDP_FIELDS = [
    ("user", "str"),
]


class RemotePanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Remote")
        self.is_client = is_client

    def _build(self):
        self.config = RemoteConfig(self.is_client)
        host_names = self.config.fetch_hosts().keys()

        section_label(self.body, "Scan Options")
        scan_options = self.config.fetch_scan_options()
        skip_steam = labeled_switch(self.body, "skip_steam", scan_options.get("skip_steam", False))
        skip_shortcut = labeled_switch(self.body, "skip_shortcut", scan_options.get("skip_shortcut", False))

        section_label(self.body, "Remotes to Load")
        remotes_editor = self.add_json_editor(self.config.fetch_remotes_to_load())

        section_label(self.body, "Defaults")
        defaults = self.config.fetch_defaults()
        moonlight_path = labeled_entry(self.body, "moonlight_client_path", defaults.get("moonlight_client_path", ""))
        rdp_exec = labeled_entry(self.body, "rdp_client_exec", defaults.get("rdp_client_exec", ""))

        section_label(self.body, "Prefer Local")
        prefer_local = labeled_switch(self.body, "prefer_local", self.config.fetch_prefer_local())

        section_label(self.body, "Prefer Exceptions")
        exceptions_editor = self.add_json_editor(self.config.fetch_prefer_exceptions())

        section_label(self.body, "Hosts")
        self.host_menu = ctk.CTkOptionMenu(
            self.body, values=list(host_names), command=self._on_select_host
        )
        self.host_menu.pack(fill="x", pady=4)
        self.host_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.host_container.pack(fill="both", expand=True, pady=4)

        def save():
            self.config.update_scan_options(
                {"skip_steam": skip_steam.get(), "skip_shortcut": skip_shortcut.get()}
            )
            self.config.update_remotes_to_load(remotes_editor.get())
            self.config.update_defaults(
                {"moonlight_client_path": moonlight_path.get(), "rdp_client_exec": rdp_exec.get()}
            )
            self.config.update_prefer_local(prefer_local.get())
            self.config.update_prefer_exceptions(exceptions_editor.get())
            self.set_status("Saved remote config")

        self.selected_host = next(iter(host_names), None)
        if self.selected_host is not None:
            self._render_host()

        self.add_save_button(save)

    # ------------------------------------------------------------------

    def _on_select_host(self, host):
        self.selected_host = host
        self._render_host()

    def _render_host(self):
        for child in self.host_container.winfo_children():
            child.destroy()

        if self.selected_host is None:
            return

        host = dict(self.config.fetch_hosts()[self.selected_host])
        widgets = {}

        def type_fields():
            fields = list(COMMON_FIELDS)
            if host.get("remote_client_type") == "moonlight":
                fields += MOONLIGHT_FIELDS
            elif host.get("remote_client_type") == "rdp":
                fields += RDP_FIELDS
            return fields

        def rebuild():
            for child in self.host_container.winfo_children():
                child.destroy()
            rt = widgets.get("remote_client_type")
            if rt is not None:
                host["remote_client_type"] = rt.get()
            render()

        def render():
            for field, field_type in type_fields():
                value = host.get(field, "")
                if field_type == "bool":
                    widgets[field] = labeled_switch(self.host_container, field, value)
                elif field_type == "selector":
                    widgets[field] = labeled_selector(
                        self.host_container,
                        field,
                        ["moonlight", "rdp"],
                        host.get(field, "moonlight"),
                    )
                    widgets[field].trace_add("write", lambda *a: rebuild())
                else:
                    widgets[field] = labeled_entry(self.host_container, field, value)

            section_label(self.host_container, "Manual")
            manual_editor = JsonEditor(self.host_container, host.get("manual", {}))
            manual_editor.pack(fill="both", expand=True)
            widgets["manual"] = manual_editor

            def save_host():
                new_host = {"remote_client_type": host.get("remote_client_type", "moonlight")}
                for field, _field_type in type_fields():
                    widget = widgets.get(field)
                    if widget is None:
                        continue
                    if _field_type == "bool":
                        new_host[field] = widget.get()
                    else:
                        new_host[field] = widget.get()
                new_host["manual"] = widgets["manual"].get()
                self.config.update_host(self.selected_host, new_host)
                self.set_status("Saved remote host")

            ctk.CTkButton(self.host_container, text="Save Host", command=save_host).pack(
                anchor="w", pady=6
            )

        render()
