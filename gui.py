"""
Echo Show Smart Display Desktop UI for JARVIS / Alexa.
Cross-platform visual dashboard with glowing animated orb, digital clock,
weather widget, active timer countdowns, and live speech subtitles.
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import datetime
import math
import threading
import time
import tkinter as tk
from tkinter import ttk

import config
import audio_engine
from skills import timer_alarm, weather, notes_reminders


class EchoShowGUI:
    """Smart Display GUI for JARVIS / Alexa."""

    def __init__(self, root, on_command_submit=None):
        self.root = root
        self.on_command_submit = on_command_submit
        self.root.title(f"{config.ASSISTANT_NAME} - Echo Show Smart Display")
        self.root.geometry("850x620")
        self.root.minsize(750, 550)
        self.root.configure(bg="#0d1117")

        self.is_running = True
        self.current_state = "idle"  # 'idle', 'listening', 'processing', 'speaking'
        self.animation_angle = 0
        self.orb_radius = 55
        self.orb_growth = 0.5

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._start_clock_thread()
        self._start_animation_loop()

        # Register observer for audio engine speech events
        audio_engine.register_speech_observer(self.update_speech_subtitle)

    def _on_close(self):
        self.is_running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def _build_ui(self):
        # 1. Top Header Bar (Clock & Weather)
        self.header_frame = tk.Frame(self.root, bg="#161b22", height=80, pady=10, padx=20)
        self.header_frame.pack(fill="x", side="top")

        # Time & Date
        self.time_label = tk.Label(
            self.header_frame,
            text="12:00 PM",
            font=("Helvetica", 28, "bold"),
            fg="#58a6ff",
            bg="#161b22"
        )
        self.time_label.pack(side="left")

        self.date_label = tk.Label(
            self.header_frame,
            text="Wednesday, August 26",
            font=("Helvetica", 12),
            fg="#8b949e",
            bg="#161b22",
            padx=15
        )
        self.date_label.pack(side="left", pady=8)

        # Weather Widget on right
        self.weather_label = tk.Label(
            self.header_frame,
            text=f"🌤️ {config.DEFAULT_CITY} Loading...",
            font=("Helvetica", 13),
            fg="#e6edf3",
            bg="#161b22"
        )
        self.weather_label.pack(side="right")

        # 2. Main Center Frame (Orb Visualizer & Subtitles)
        self.center_frame = tk.Frame(self.root, bg="#0d1117")
        self.center_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Canvas for Animated Glowing Orb
        self.canvas = tk.Canvas(
            self.center_frame,
            width=220,
            height=180,
            bg="#0d1117",
            highlightthickness=0
        )
        self.canvas.pack(pady=5)

        # Assistant Status Text
        self.status_label = tk.Label(
            self.center_frame,
            text="Ready • Say 'Alexa' or 'Jarvis'",
            font=("Helvetica", 14, "bold"),
            fg="#3fb950",
            bg="#0d1117"
        )
        self.status_label.pack(pady=5)

        # Subtitles Text Box
        self.subtitles_box = tk.Text(
            self.center_frame,
            height=4,
            width=70,
            font=("Helvetica", 13),
            fg="#c9d1d9",
            bg="#161b22",
            bd=0,
            padx=15,
            pady=10,
            wrap="word"
        )
        self.subtitles_box.insert("1.0", "Welcome! Speak your command or type below...")
        self.subtitles_box.config(state="disabled")
        self.subtitles_box.pack(pady=10)

        # 3. Active Timers & Quick Stats Card
        self.timers_frame = tk.Frame(self.center_frame, bg="#0d1117")
        self.timers_frame.pack(fill="x", pady=5)

        self.timer_card = tk.Label(
            self.timers_frame,
            text="⏱️ No Active Timers",
            font=("Helvetica", 11),
            fg="#8b949e",
            bg="#161b22",
            padx=15,
            pady=6
        )
        self.timer_card.pack(side="left", padx=5)

        # 4. Quick Actions Toolbar
        self.quick_frame = tk.Frame(self.root, bg="#0d1117", pady=5)
        self.quick_frame.pack(fill="x", padx=20)

        quick_actions = [
            ("🌅 Good Morning", "start my day"),
            ("🎯 Focus Mode", "focus mode"),
            ("🌤️ Weather", "what is the weather"),
            ("📰 Tech News", "tech news"),
            ("😂 Tell Joke", "tell me a joke"),
            ("🪙 Flip Coin", "flip a coin")
        ]

        for label, cmd in quick_actions:
            btn = tk.Button(
                self.quick_frame,
                text=label,
                font=("Helvetica", 10, "bold"),
                bg="#21262d",
                fg="#58a6ff",
                activebackground="#30363d",
                activeforeground="#ffffff",
                relief="flat",
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda c=cmd: self._send_command(c)
            )
            btn.pack(side="left", padx=4)

        # 5. Bottom Input Bar
        self.bottom_frame = tk.Frame(self.root, bg="#161b22", height=60, pady=10, padx=20)
        self.bottom_frame.pack(fill="x", side="bottom")

        self.entry = tk.Entry(
            self.bottom_frame,
            font=("Helvetica", 13),
            bg="#0d1117",
            fg="#f0f6fc",
            insertbackground="#58a6ff",
            relief="flat",
            bd=5
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self._on_enter())

        self.send_btn = tk.Button(
            self.bottom_frame,
            text="Send ➔",
            font=("Helvetica", 11, "bold"),
            bg="#238636",
            fg="#ffffff",
            activebackground="#2ea043",
            relief="flat",
            padx=15,
            pady=4,
            cursor="hand2",
            command=self._on_enter
        )
        self.send_btn.pack(side="right")

    def _on_enter(self):
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, tk.END)
            self._send_command(text)

    def _send_command(self, cmd: str):
        self.update_speech_subtitle(f"You: {cmd}", state="processing")
        if self.on_command_submit:
            threading.Thread(target=self.on_command_submit, args=(cmd,), daemon=True).start()

    def update_speech_subtitle(self, text: str, state: str = "idle"):
        """Updates GUI subtitles and animation state."""
        if not self.is_running:
            return
        self.current_state = state

        def _update():
            if not self.is_running:
                return
            try:
                if state == "listening":
                    self.status_label.config(text="🎙️ Listening...", fg="#388bfd")
                elif state == "processing":
                    self.status_label.config(text="⚡ Processing Intent...", fg="#d29922")
                elif state == "speaking":
                    self.status_label.config(text="💬 Speaking...", fg="#a371f7")
                else:
                    self.status_label.config(text="Ready • Say 'Alexa' or 'Jarvis'", fg="#3fb950")

                if text:
                    self.subtitles_box.config(state="normal")
                    self.subtitles_box.delete("1.0", tk.END)
                    self.subtitles_box.insert("1.0", text)
                    self.subtitles_box.config(state="disabled")
            except Exception:
                pass

        try:
            self.root.after(0, _update)
        except Exception:
            pass

    def _start_clock_thread(self):
        def _clock_worker():
            short_w = f"Weather in {config.DEFAULT_CITY}"
            try:
                short_w = weather.get_weather().split(".")[0]
            except Exception:
                pass

            while self.is_running:
                now = datetime.datetime.now()
                time_str = now.strftime("%I:%M:%S %p")
                date_str = now.strftime("%A, %B %d, %Y")
                
                try:
                    timer_str = timer_alarm.get_timers_status()
                except Exception:
                    timer_str = "⏱️ No Active Timers"

                if not self.is_running:
                    break

                try:
                    self.root.after(0, lambda t=time_str, d=date_str, w=short_w, ts=timer_str: self._update_clock_ui(t, d, w, ts))
                except Exception:
                    break
                time.sleep(1)

        threading.Thread(target=_clock_worker, daemon=True).start()

    def _update_clock_ui(self, time_str, date_str, weather_str, timer_str):
        if not self.is_running:
            return
        try:
            self.time_label.config(text=time_str)
            self.date_label.config(text=date_str)
            self.weather_label.config(text=f"🌤️ {weather_str}")
            self.timer_card.config(text=f"⏱️ {timer_str}")
        except Exception:
            pass

    def _start_animation_loop(self):
        """Draws dynamic pulsating glowing Alexa orb."""
        if not self.is_running:
            return
        try:
            self.canvas.delete("all")
            cx, cy = 110, 90

            # Dynamic radius based on state
            if self.current_state == "listening":
                self.orb_radius += self.orb_growth * 1.5
                if self.orb_radius > 68 or self.orb_radius < 50:
                    self.orb_growth = -self.orb_growth
                color_inner = "#58a6ff"
                color_outer = "#1f6feb"
            elif self.current_state == "speaking":
                self.orb_radius += self.orb_growth * 2.0
                if self.orb_radius > 72 or self.orb_radius < 48:
                    self.orb_growth = -self.orb_growth
                color_inner = "#bc8cff"
                color_outer = "#8957e5"
            else:
                self.orb_radius += self.orb_growth * 0.4
                if self.orb_radius > 58 or self.orb_radius < 52:
                    self.orb_growth = -self.orb_growth
                color_inner = "#238636"
                color_outer = "#2ea043"

            # Outer glow circle
            self.canvas.create_oval(
                cx - self.orb_radius - 12, cy - self.orb_radius - 12,
                cx + self.orb_radius + 12, cy + self.orb_radius + 12,
                fill="", outline=color_outer, width=2
            )

            # Core animated circle
            self.canvas.create_oval(
                cx - self.orb_radius, cy - self.orb_radius,
                cx + self.orb_radius, cy + self.orb_radius,
                fill=color_inner, outline=""
            )

            # Orbiting particle
            self.animation_angle = (self.animation_angle + 6) % 360
            rad = math.radians(self.animation_angle)
            px = cx + (self.orb_radius + 18) * math.cos(rad)
            py = cy + (self.orb_radius + 18) * math.sin(rad)
            self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill="#ffffff", outline="")

            self.root.after(40, self._start_animation_loop)
        except Exception:
            pass


def launch_gui(on_command_cb=None):
    """Launches the Echo Show Smart Display UI."""
    root = tk.Tk()
    app = EchoShowGUI(root, on_command_submit=on_command_cb)
    root.mainloop()


if __name__ == "__main__":
    import jarvis
    launch_gui(on_command_cb=jarvis.execute_intent)
