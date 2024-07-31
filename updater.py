import requests
from tkinter import messagebox
import threading
import time


class Updater:
    def __init__(self, current_version, master=None):
        self.current_version = current_version
        self.master = master
        self.github_api_url = (
            "https://api.github.com/repos/depleur/patience/releases/latest"
        )
        self.update_thread = None
        self.stop_thread = False

    def check_for_updates(self):
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release["tag_name"]

            if self.is_newer_version(latest_version):
                self.notify_update_available(latest_version, latest_release["html_url"])
                return True
            return False
        except requests.RequestException:
            print("Failed to check for updates")
            return False

    def is_newer_version(self, latest_version):
        current = [x for x in self.current_version[1:].split(".")]
        latest = [x for x in latest_version[1:].split(".")]
        return latest > current

    def notify_update_available(self, new_version, download_url):
        if self.master:
            self.master.after(
                0,
                lambda: messagebox.showinfo(
                    "Update Available",
                    f"A new version ({new_version}) is available!\n"
                    f"You can download it from:\n{download_url}",
                ),
            )
        else:
            print(f"A new version ({new_version}) is available!")
            print(f"You can download it from: {download_url}")

    def start_update_check_thread(self):
        self.update_thread = threading.Thread(target=self.periodic_update_check)
        self.update_thread.start()

    def stop_update_check_thread(self):
        self.stop_thread = True
        if self.update_thread:
            self.update_thread.join()

    def periodic_update_check(self):
        while not self.stop_thread:
            self.check_for_updates()
            time.sleep(3600)  # Sleep for 1 hour
