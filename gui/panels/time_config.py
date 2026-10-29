from gui.panels.base import BasePanel
from gui.widgets import labeled_entry, labeled_switch, section_label
from lib.config import read_json, write_json

CONFIG_PATH = "./config/time_config.json"


class TimeConfigPanel(BasePanel):
    def __init__(self, master, is_client=False):
        super().__init__(master, "Time Config")
        self.is_client = is_client

    def _build(self):
        data = read_json(CONFIG_PATH, self.is_client)

        section_label(self.body, "Messages")
        no_time = labeled_entry(self.body, "No time to play", data.get("no_time_to_play", ""))
        limit_reached = labeled_entry(self.body, "Time limit reached", data.get("time_limit_reached", ""))

        section_label(self.body, "Limits & Hooks")
        first_time = labeled_entry(self.body, "First warning time", data.get("first_warning_time", ""))
        first_hook = labeled_entry(self.body, "First warning hook", data.get("first_warning_hook", ""))
        final_time = labeled_entry(self.body, "Final warning time", data.get("final_warning_time", ""))
        final_hook = labeled_entry(self.body, "Final warning hook", data.get("final_warning_hook", ""))

        section_label(self.body, "Trigger & Tracking")
        trigger = labeled_entry(self.body, "Time saver trigger", data.get("time_saver_trigger", ""))
        tracker = labeled_entry(self.body, "Time tracker URL", data.get("time_tracker_url", ""))
        whitelisted = labeled_entry(self.body, "Whitelisted days", ", ".join(data.get("whitelisted_days", [])))

        def save():
            new_data = dict(data)
            new_data["no_time_to_play"] = no_time.get()
            new_data["time_limit_reached"] = limit_reached.get()
            new_data["first_warning_time"] = _to_number(first_time.get())
            new_data["first_warning_hook"] = first_hook.get()
            new_data["final_warning_time"] = _to_number(final_time.get())
            new_data["final_warning_hook"] = final_hook.get()
            new_data["time_saver_trigger"] = trigger.get()
            new_data["time_tracker_url"] = tracker.get()
            new_data["whitelisted_days"] = [
                item.strip() for item in whitelisted.get().split(",") if item.strip()
            ]
            write_json(CONFIG_PATH, new_data, self.is_client)
            self.set_status("Saved time config")

        self.add_save_button(save)


def _to_number(value):
    try:
        if "." in value or "e" in value.lower():
            return float(value)
        return int(value)
    except ValueError:
        return value
