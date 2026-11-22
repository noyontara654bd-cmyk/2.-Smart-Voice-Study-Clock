import tkinter as tk
from tkinter import messagebox
import datetime
import threading
import pyttsx3
import winsound

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 165)  # Speed of speech

def speak_reminder(message):
    """Plays an alarm beep and speaks the reminder message in a background thread."""
    def run():
        try:
            # Play a short beep sound (frequency 1000Hz, duration 500ms)
            winsound.Beep(1000, 500)
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print("Audio error:", e)
    threading.Thread(target=run, daemon=True).start()

class StudyClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Voice Study Clock By MARIA")
        self.root.geometry("780x480")
        self.root.configure(bg="#E6E0F8")  # Soft powder purple background

        self.schedule = []  # List to store study sessions
        self.announced_events = set()  # Track spoken alerts so they don't repeat

        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        # Title Header
        title_label = tk.Label(
            self.root, text="Smart Study Schedule & Voice Clock",
            font=("Helvetica", 18, "bold"), bg="#E6E0F8", fg="#3B235A"
        )
        title_label.pack(pady=15)

        # Main Container (Left: Schedule Input & List, Right: Live Clock & Status)
        main_frame = tk.Frame(self.root, bg="#E6E0F8")
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # --- LEFT SIDE: Subject & Time Input ---
        left_frame = tk.Frame(main_frame, bg="#F5F2FC", bd=2, relief="groove")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        tk.Label(left_frame, text="Add Study Subject", font=("Helvetica", 13, "bold"), bg="#F5F2FC", fg="#4A2C70").pack(pady=10)

        # Subject Name Input
        tk.Label(left_frame, text="Subject Name:", bg="#F5F2FC", font=("Helvetica", 10)).pack(anchor="w", padx=15)
        self.subject_entry = tk.Entry(left_frame, font=("Helvetica", 11), width=28)
        self.subject_entry.pack(padx=15, pady=(0, 8))

        # Start Time Input (24-hour format HH:MM)
        tk.Label(left_frame, text="Start Time (HH:MM in 24h, e.g., 21:30):", bg="#F5F2FC", font=("Helvetica", 10)).pack(anchor="w", padx=15)
        self.start_entry = tk.Entry(left_frame, font=("Helvetica", 11), width=28)
        self.start_entry.pack(padx=15, pady=(0, 8))

        # End Time Input (24-hour format HH:MM)
        tk.Label(left_frame, text="End Time (HH:MM in 24h, e.g., 22:30):", bg="#F5F2FC", font=("Helvetica", 10)).pack(anchor="w", padx=15)
        self.end_entry = tk.Entry(left_frame, font=("Helvetica", 11), width=28)
        self.end_entry.pack(padx=15, pady=(0, 12))

        # Add Button
        add_btn = tk.Button(
            left_frame, text="+ Add to Routine", font=("Helvetica", 11, "bold"),
            bg="#7E57C2", fg="white", command=self.add_subject, cursor="hand2"
        )
        add_btn.pack(pady=5)

        # Schedule Listbox
        tk.Label(left_frame, text="Today's Routine:", bg="#F5F2FC", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        self.routine_listbox = tk.Listbox(left_frame, font=("Helvetica", 10), height=7, width=34)
        self.routine_listbox.pack(padx=15, pady=(0, 10))

        # --- RIGHT SIDE: Live Digital Clock & Active Status ---
        right_frame = tk.Frame(main_frame, bg="#D1C4E9", bd=2, relief="groove")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        tk.Label(right_frame, text="Current Time", font=("Helvetica", 13, "bold"), bg="#D1C4E9", fg="#311B92").pack(pady=(25, 5))

        self.clock_label = tk.Label(right_frame, text="00:00:00", font=("Helvetica", 32, "bold"), bg="#D1C4E9", fg="#1A237E")
        self.clock_label.pack(pady=10)

        self.status_title = tk.Label(right_frame, text="Current Session:", font=("Helvetica", 12, "bold"), bg="#D1C4E9", fg="#4A148C")
        self.status_title.pack(pady=(20, 5))

        self.active_subject_label = tk.Label(
            right_frame, text="No active subject right now",
            font=("Helvetica", 13, "bold"), bg="#D1C4E9", fg="#212121", wraplength=280
        )
        self.active_subject_label.pack(pady=5)

        self.countdown_label = tk.Label(
            right_frame, text="Remaining: ...........",
            font=("Helvetica", 14), bg="#D1C4E9", fg="#B71C1C"
        )
        self.countdown_label.pack(pady=15)

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        start_str = self.start_entry.get().strip()
        end_str = self.end_entry.get().strip()

        if not subject or not start_str or not end_str:
            messagebox.showwarning("Input Error", "Please fill in all fields!")
            return

        try:
            today = datetime.date.today()
            start_time = datetime.datetime.combine(today, datetime.datetime.strptime(start_str, "%H:%M").time())
            end_time = datetime.datetime.combine(today, datetime.datetime.strptime(end_str, "%H:%M").time())

            if end_time <= start_time:
                messagebox.showerror("Time Error", "End time must be after start time!")
                return

            self.schedule.append({
                "Subject": subject,
                "Start": start_time,
                "End": end_time
            })
            # Sort schedule by start time
            self.schedule.sort(key=lambda x: x["start"])

            self.refresh_listbox()
            self.subject_entry.delete(0, tk.END)
            self.start_entry.delete(0, tk.END)
            self.end_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Format Error", "Please enter time in HH:MM format (e.g., 21:30).")

    def refresh_listbox(self):
        self.routine_listbox.delete(0, tk.END)
        for item in self.schedule:
            s_str = item["start"].strftime("%H:%M")
            e_str = item["end"].strftime("%H:%M")
            self.routine_listbox.insert(tk.END, f"{s_str} - {e_str}  |  {item['subject']}")

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))

        active_found = False

        for idx, item in enumerate(self.schedule):
            subj = item["subject"]
            start = item["start"]
            end = item["end"]

            # Check if session is currently running
            if start <= now < end:
                active_found = True
                remaining = end - now
                rem_seconds = int(remaining.total_seconds())

                # Format remaining time
                hours, remainder = divmod(rem_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.active_subject_label.config(text=f"Studying: {subj}")
                self.countdown_label.config(text=f"Time Left: {hours:02d}:{minutes:02d}:{seconds:02d}")

                # 1. Start Announcement
                start_key = f"{idx}_start"
                if start_key not in self.announced_events and (now - start).total_seconds() < 5:
                    self.announced_events.add(start_key)
                    speak_reminder(f"This {subj} study time starts now.")

                # 2. 1 Hour Left Announcement
                one_hr_key = f"{idx}_1hr"
                if one_hr_key not in self.announced_events and 3595 <= rem_seconds <= 3600:
                    self.announced_events.add(one_hr_key)
                    speak_reminder(f"1 hour left for {subj}.")

                # 3. 30 Minutes Left Announcement
                thirty_min_key = f"{idx}_30min"
                if thirty_min_key not in self.announced_events and 1795 <= rem_seconds <= 1800:
                    self.announced_events.add(thirty_min_key)
                    speak_reminder(f"30 minutes left for {subj}.")

            # 4. End Time Announcement (within 3 seconds after end time)
            end_key = f"{idx}_end"
            if end_key not in self.announced_events and 0 <= (now - end).total_seconds() < 3:
                self.announced_events.add(end_key)
                # Check if there is a next subject starting right now
                next_subj_msg = ""
                if idx + 1 < len(self.schedule):
                    next_subj = self.schedule[idx + 1]["subject"]
                    next_subj_msg = f" Starting next subject, {next_subj}."
                speak_reminder(f"End time for {subj}.{next_subj_msg}")

        if not active_found:
            self.active_subject_label.config(text="No active subject right now")
            self.countdown_label.config(text="Remaining: ...........")

        # Refresh every 1000ms (1 second)
        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyClockApp(root)
    root.mainloop()
