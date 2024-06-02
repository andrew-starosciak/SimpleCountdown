import json
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

import sys
import os
from loguru import logger as log
from datetime import datetime, timedelta

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

# Import globals
import globals as gl

# Import own modules
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page

class DigitalCountdown(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.HAS_CONFIGURATION = True
        
        self.total_minutes = 10  # Default to a 10-minute countdown
        self.end_time = None
        self.is_running = False

    def on_ready(self):
        self.show()

    def get_config_rows(self) -> list:
        self.total_minutes_entry = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.digital-countdown.total-minutes"),
            tooltip_text=self.plugin_base.lm.get("actions.digital-countdown.total-minutes.tooltip")
        )

        self.load_defaults()

        self.total_minutes_entry.connect("changed", self.on_total_minutes_entry_changed)

        return [self.total_minutes_entry]
    
    def load_defaults(self):
        settings = self.get_settings()

        total_minutes_str = settings.get("total-minutes", str(self.total_minutes))
        self.total_minutes_entry.set_text(total_minutes_str)
        self.total_minutes = int(total_minutes_str)

    def on_total_minutes_entry_changed(self, *args):
        settings = self.get_settings()
        total_minutes_str = self.total_minutes_entry.get_text()

        try:
            self.total_minutes = int(total_minutes_str)
            settings["total-minutes"] = total_minutes_str
            self.set_settings(settings)
            self.show()
        except ValueError:
            log.error("Invalid total minutes format")

    def on_key_down(self):
        self.start_countdown()

    def start_countdown(self):
        self.end_time = datetime.now() + timedelta(minutes=self.total_minutes)
        self.is_running = True
        self.show()

    def on_tick(self):
        if self.is_running:
            self.show()

    def show(self):
        if not self.is_running or not self.end_time:
            self.set_top_label("00:00:00")
            return
        
        now = datetime.now()
        remaining_time = self.end_time - now

        if remaining_time.total_seconds() < 0:
            remaining_time = timedelta(0)  # Set to zero if time has passed
            self.is_running = False  # Stop the countdown

        total_seconds = int(remaining_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.set_top_label(time_str)

class ClocksPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.init_locale_manager()

        self.lm = self.locale_manager

        ## Register actions
        self.digital_countdown_holder = ActionHolder(
            plugin_base=self,
            action_base=DigitalCountdown,
            action_id="com_core447_Clocks::DigitalCountdown",
            action_name=self.lm.get("actions.digital-countdown.name")
        )
        self.add_action_holder(self.digital_countdown_holder)

        # Register plugin
        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/StreamController/Clocks",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )

    def init_locale_manager(self):
        self.lm = self.locale_manager
        self.lm.set_to_os_default()

    def get_selector_icon(self) -> Gtk.Widget:
        return Gtk.Image(icon_name="preferences-system-time-symbolic")




