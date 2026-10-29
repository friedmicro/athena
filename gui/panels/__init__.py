from gui.panels.base import BasePanel
from gui.panels.accessibility import AccessibilityPanel
from gui.panels.android import AndroidPanel
from gui.panels.client import ClientPanel
from gui.panels.combiner import CombinerPanel
from gui.panels.emulators import EmulatorsPanel
from gui.panels.local import LocalPanel
from gui.panels.manual import ManualPanel
from gui.panels.overrides import OverridesPanel
from gui.panels.remote import RemotePanel
from gui.panels.steam import SteamPanel
from gui.panels.time_config import TimeConfigPanel
from gui.panels.web import WebPanel
from gui.panels.windows_games import WindowsGamesPanel

CONFIG_PANELS = [
    ("Client", ClientPanel),
    ("Remote", RemotePanel),
    ("Steam", SteamPanel),
    ("Emulators", EmulatorsPanel),
    ("Web", WebPanel),
    ("Combiner", CombinerPanel),
    ("Windows Games", WindowsGamesPanel),
    ("Accessibility", AccessibilityPanel),
    ("Time Config", TimeConfigPanel),
    ("Android", AndroidPanel),
    ("Local", LocalPanel),
    ("Overrides", OverridesPanel),
    ("Manual", ManualPanel),
]

__all__ = [
    "BasePanel",
    "CONFIG_PANELS",
    "AccessibilityPanel",
    "AndroidPanel",
    "ClientPanel",
    "CombinerPanel",
    "EmulatorsPanel",
    "LocalPanel",
    "ManualPanel",
    "OverridesPanel",
    "RemotePanel",
    "SteamPanel",
    "TimeConfigPanel",
    "WebPanel",
    "WindowsGamesPanel",
]
