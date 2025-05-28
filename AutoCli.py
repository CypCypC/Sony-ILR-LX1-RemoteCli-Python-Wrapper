import subprocess
import threading
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

#Change this path to your RemoteCli
REMOTECLI_PATH = "E:\\toutcequiestcour\\UPSSITECH\\stage\\camera\\build_vs\\Release\\RemoteCli.exe"

class RemoteCliApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sony RemoteCli Controller")

        self.proc = None
        self.auto_running = False
        self.auto_thread = None

        # Output display
        self.output = ScrolledText(root, height=25, width=100, state="disabled")
        self.output.pack()

        # Manual command input
        self.entry = tk.Entry(root, width=80)
        self.entry.pack(side="left", padx=5, pady=5)
        self.entry.bind("<Return>", self.send_command)

        # Action buttons
        tk.Button(root, text="Send", command=self.send_command).pack(side="left")
        tk.Button(root, text="Focus", command=self.automate_focus).pack(side="left")
        tk.Button(root, text="Focus + Photo", command=self.automate_focus_and_photo).pack(side="left")
        tk.Button(root, text="Auto Capture", command=self.toggle_auto).pack(side="left")
        tk.Button(root, text="Exit", command=self.exit_program).pack(side="left")

        self.log("Application ready. Launching RemoteCli.exe...")
        self.launch_remotecli()

    def launch_remotecli(self):
        self.proc = subprocess.Popen(
            REMOTECLI_PATH,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        threading.Thread(target=self.read_stdout, daemon=True).start()

    def read_stdout(self):
        for line in self.proc.stdout:
            self.log(line)

    def log(self, message):
        self.output.config(state="normal")
        self.output.insert(tk.END, message)
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def send(self, cmd, delay=0.5):
        """Send a command to RemoteCli with an optional delay."""
        if self.proc:
            self.proc.stdin.write(cmd + "\n")
            self.proc.stdin.flush()
            time.sleep(delay)

    def send_command(self, event=None):
        """Send manual input from the text field to RemoteCli."""
        cmd = self.entry.get().strip()
        if cmd:
            self.send(cmd)
            self.entry.delete(0, tk.END)

    def navigate_to_shutter_menu(self):
        """Enter the Shutter/Rec Operation Menu."""
        self.send("1")

    def exit_shutter_menu(self):
        """Exit the Shutter/Rec Operation Menu back to the main menu."""
        self.send("0")

    def automate_focus(self):
        """Perform autofocus."""
        self.log("Running autofocus...")
        self.navigate_to_shutter_menu()
        self.send("2")  # Half-press shutter
        self.send("y")  # Confirm
        self.exit_shutter_menu()
        self.log("Focus complete.")

    def automate_focus_and_photo(self):
        """Perform autofocus followed by photo capture."""
        self.log("Running autofocus and photo capture...")
        self.navigate_to_shutter_menu()
        self.send("3")  # Half + full press
        self.send("y")  # Confirm
        self.exit_shutter_menu()
        self.log("Focus and photo complete.")

    def toggle_auto(self):
        """Start or stop automatic photo capture every second."""
        if not self.auto_running:
            self.auto_running = True
            self.log("Auto capture started (1 photo per second).")
            self.auto_thread = threading.Thread(target=self.auto_capture, daemon=True)
            self.auto_thread.start()
        else:
            self.auto_running = False
            self.log("Auto capture paused.")

    def auto_capture(self):
        """Continuously take photos at 1-second intervals."""
        while self.auto_running:
            self.navigate_to_shutter_menu()
            self.send("1")  # Trigger photo
            self.exit_shutter_menu()
            time.sleep(1)

    def exit_program(self):
        """Gracefully terminate RemoteCli and exit the application."""
        self.auto_running = False
        if self.proc:
            try:
                self.send("x")
                self.proc.terminate()
            except:
                pass
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteCliApp(root)
    root.mainloop()
