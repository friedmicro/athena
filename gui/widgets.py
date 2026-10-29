import json
import os

import customtkinter as ctk

class JsonEditor(ctk.CTkFrame):
    def __init__(self, master, value, fg_color="transparent"):
        super().__init__(master, fg_color=fg_color)
        self._build(value)

    def _build(self, value):
        if isinstance(value, bool):
            self._var = ctk.BooleanVar(value=value)
            self._control = ctk.CTkSwitch(self, text="", variable=self._var)
            self._control.pack(anchor="w")
            self.get = lambda: self._var.get()
        elif isinstance(value, (int, float)):
            self._var = ctk.StringVar(value=str(value))
            self._control = ctk.CTkEntry(self, textvariable=self._var, width=220)
            self._control.pack(fill="x")
            self.get = lambda: _coerce_number(self._var.get())
        elif isinstance(value, str):
            self._var = ctk.StringVar(value=value)
            self._control = ctk.CTkEntry(self, textvariable=self._var, width=220)
            self._control.pack(fill="x")
            self.get = lambda: self._var.get()
        elif isinstance(value, list):
            self._control = _ListEditor(self, value)
            self._control.pack(fill="x", expand=True)
            self.get = self._control.get_value
        elif isinstance(value, dict):
            self._control = _DictEditor(self, value)
            self._control.pack(fill="x", expand=True)
            self.get = self._control.get_value
        else:
            self._var = ctk.StringVar(value="")
            self._control = ctk.CTkEntry(self, textvariable=self._var, width=220)
            self._control.pack(fill="x")
            self.get = lambda: None

    def get(self):
        raise NotImplementedError("overridden in _build")


def _coerce_number(text):
    try:
        if "." in text or "e" in text.lower():
            return float(text)
        return int(text)
    except ValueError:
        return text


class _ListEditor(ctk.CTkFrame):
    def __init__(self, master, value, fg_color="transparent"):
        super().__init__(master, fg_color=fg_color)
        self._rows = []
        self._add_btn = ctk.CTkButton(self, text="+ add item", width=90)
        self._add_btn.configure(command=self._append_new_row)
        for item in value:
            self._append_row(item)
        self._add_btn.pack(anchor="w", pady=2)

    def _append_row(self, value):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=1)
        editor = JsonEditor(row, value)
        editor.pack(side="left", fill="x", expand=True, padx=(0, 4))
        del_btn = ctk.CTkButton(row, text="x", width=26, fg_color="gray30",
                                command=lambda: self._delete_row(row))
        del_btn.pack(side="right")
        self._rows.append((row, editor))

    def _append_new_row(self):
        self._append_row("")

    def _delete_row(self, row):
        row.destroy()
        self._rows = [r for r in self._rows if r[0] != row]

    def get_value(self):
        return [editor.get() for _row, editor in self._rows]


class _DictEditor(ctk.CTkFrame):
    def __init__(self, master, value, fg_color="transparent"):
        super().__init__(master, fg_color=fg_color)
        self._rows = []
        self._add_btn = ctk.CTkButton(self, text="+ add key", width=90)
        self._add_btn.configure(command=self._append_new_row)
        for key, item in value.items():
            self._append_row(key, item)
        self._add_btn.pack(anchor="w", pady=2)

    def _append_row(self, key, value):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=1)
        key_var = ctk.StringVar(value=str(key))
        key_entry = ctk.CTkEntry(row, textvariable=key_var, width=150)
        key_entry.pack(side="left", padx=(0, 4))
        editor = JsonEditor(row, value)
        editor.pack(side="left", fill="x", expand=True, padx=(0, 4))
        del_btn = ctk.CTkButton(row, text="x", width=26, fg_color="gray30",
                                command=lambda: self._delete_row(row))
        del_btn.pack(side="right")
        self._rows.append((row, key_var, editor))

    def _append_new_row(self):
        self._append_row("key", "")

    def _delete_row(self, row):
        row.destroy()
        self._rows = [r for r in self._rows if r[0] != row]

    def get_value(self):
        result = {}
        for _row, key_var, editor in self._rows:
            result[key_var.get()] = editor.get()
        return result


def section_label(parent, text):
    """A bold section heading used to group related form fields."""
    label = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=16, weight="bold"))
    label.pack(anchor="w", pady=(8, 2))
    return label


def labeled_entry(parent, label, value=""):
    """A row with a fixed-width label and a text entry.

    Returns the associated :class:`tkinter.StringVar` for reading the value.
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=2)
    lbl = ctk.CTkLabel(row, text=label, width=200, anchor="w")
    lbl.pack(side="left")
    var = ctk.StringVar(value="" if value is None else str(value))
    entry = ctk.CTkEntry(row, textvariable=var)
    entry.pack(side="left", fill="x", expand=True)
    return var


def labeled_switch(parent, label, value=False):
    """A row with a fixed-width label and an on/off switch.

    Returns the associated :class:`tkinter.BooleanVar` for reading the value.
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=2)
    lbl = ctk.CTkLabel(row, text=label, width=200, anchor="w")
    lbl.pack(side="left")
    var = ctk.BooleanVar(value=bool(value))
    switch = ctk.CTkSwitch(row, text="", variable=var)
    switch.pack(side="left")
    return var


def labeled_selector(parent, label, values, default=None):
    """A row with a fixed-width label and an option menu.

    Returns the associated :class:`tkinter.StringVar` for reading the value.
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=2)
    lbl = ctk.CTkLabel(row, text=label, width=200, anchor="w")
    lbl.pack(side="left")
    var = ctk.StringVar(value=default if default is not None else "")
    menu = ctk.CTkOptionMenu(row, values=list(values), variable=var)
    menu.pack(side="left", fill="x", expand=True)
    return var


def save_button(parent, text="Save", command=None):
    btn = ctk.CTkButton(parent, text=text, command=command)
    btn.pack(anchor="w", pady=6)
    return btn


CONFIG_FILES = [
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


def client_directory(client_id):
    return os.path.join("config", "clients", client_id)


def client_config_path(client_id, filename):
    return os.path.join(client_directory(client_id), filename)


def list_client_ids():
    """Return the ids of configured client folders (if any)."""
    base = os.path.join("config", "clients")
    if not os.path.isdir(base):
        return []
    return [d for d in sorted(os.listdir(base))
            if os.path.isdir(os.path.join(base, d))]


def read_client_file(client_id, filename):
    path = client_config_path(client_id, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as handle:
        return json.load(handle)


def write_client_file(client_id, filename, data):
    path = client_config_path(client_id, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        json.dump(data, handle, indent=4)


def client_files_for(client_id):
    """Config files present in the given client's folder."""
    directory = client_directory(client_id)
    if not os.path.isdir(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith(".json"))
