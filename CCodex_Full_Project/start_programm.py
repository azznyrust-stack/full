import json
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


class StartProgrammApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CCodex Startprogramm")
        self.root.geometry("1080x680")
        self.root.configure(bg="#050a12")
        self.root.minsize(980, 620)

        self.process: subprocess.Popen | None = None
        self.is_running = False

        self.layout_var = tk.StringVar(value="config/layout.json")
        self.fps_var = tk.StringVar(value="5")
        self.db_path_var = tk.StringVar(value="output/farm.db")
        self.snapshot_var = tk.StringVar(value="1.0")

        self.debug_var = tk.BooleanVar(value=True)
        self.debug_ocr_var = tk.BooleanVar(value=False)
        self.db_var = tk.BooleanVar(value=False)

        self.window_title_var = tk.StringVar(value="-")
        self.status_var = tk.StringVar(value="Bereit")
        self.last_snapshot_var = tk.StringVar(value="Noch kein Snapshot")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#050a12")
        top.pack(fill="both", expand=True, padx=18, pady=18)

        left_col = tk.Frame(top, bg="#050a12")
        left_col.pack(side="left", fill="both", expand=True)

        right_col = tk.Frame(top, bg="#050a12", width=300)
        right_col.pack(side="right", fill="y", padx=(14, 0))

        self._build_brand_card(left_col)
        self._build_controls_card(left_col)
        self._build_log_card(left_col)
        self._build_status_column(right_col)

    def _make_card(self, parent, title: str, height: int | None = None):
        card = tk.Frame(parent, bg="#0b111b", highlightbackground="#14f2b0", highlightthickness=2)
        if height:
            card.configure(height=height)
            card.pack_propagate(False)
        card.pack(fill="x", pady=(0, 12))

        label = tk.Label(
            card,
            text=title,
            bg="#0b111b",
            fg="#d8dde7",
            font=("Bahnschrift", 14, "bold"),
            anchor="w",
        )
        label.pack(fill="x", padx=12, pady=(10, 8))
        return card

    def _build_brand_card(self, parent):
        card = self._make_card(parent, "LIVE FARM ANALYTICS", height=120)
        row = tk.Frame(card, bg="#0b111b")
        row.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        tk.Label(row, text="CCODEX", bg="#0b111b", fg="#14f2b0", font=("Bahnschrift", 38, "bold")).pack(side="left")
        tk.Label(row, text="STARTPANEL", bg="#0b111b", fg="#d8dde7", font=("Bahnschrift", 24, "bold")).pack(side="left", padx=(12, 0), pady=(10, 0))

    def _build_controls_card(self, parent):
        card = self._make_card(parent, "STARTKONFIGURATION")
        body = tk.Frame(card, bg="#0b111b")
        body.pack(fill="x", padx=12, pady=(0, 12))

        self._entry_row(body, "Layout", self.layout_var, browse=True)
        self._entry_row(body, "FPS", self.fps_var)
        self._entry_row(body, "Snapshot-Intervall", self.snapshot_var)
        self._entry_row(body, "DB-Pfad", self.db_path_var)

        options = tk.Frame(body, bg="#0b111b")
        options.pack(fill="x", pady=(6, 12))
        self._styled_check(options, "Debug ROI", self.debug_var).pack(side="left", padx=(0, 18))
        self._styled_check(options, "Debug OCR", self.debug_ocr_var).pack(side="left", padx=(0, 18))
        self._styled_check(options, "SQLite", self.db_var).pack(side="left")

        buttons = tk.Frame(body, bg="#0b111b")
        buttons.pack(fill="x")
        self.start_btn = self._neon_button(buttons, "ANALYSE STARTEN", self.start_process)
        self.start_btn.pack(side="left", padx=(0, 10))
        self.stop_btn = self._neon_button(buttons, "STOP", self.stop_process, color="#ff4a6b")
        self.stop_btn.pack(side="left")
        self.stop_btn.configure(state="disabled")

    def _build_log_card(self, parent):
        card = self._make_card(parent, "LIVE-LOG", height=350)
        self.log_box = tk.Text(
            card,
            bg="#060b12",
            fg="#14f2b0",
            insertbackground="#14f2b0",
            font=("Consolas", 11),
            relief="flat",
            padx=10,
            pady=10,
            wrap="word",
        )
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log("Startprogramm bereit.")

    def _build_status_column(self, parent):
        card1 = self._make_card(parent, "STATUS", height=150)
        wrap = tk.Frame(card1, bg="#0b111b")
        wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tk.Label(wrap, textvariable=self.status_var, bg="#0b111b", fg="#14f2b0", font=("Bahnschrift", 28, "bold")).pack(anchor="w")
        tk.Label(wrap, textvariable=self.window_title_var, bg="#0b111b", fg="#d8dde7", font=("Bahnschrift", 12)).pack(anchor="w", pady=(6, 0))

        card2 = self._make_card(parent, "LETZTER SNAPSHOT", height=180)
        tk.Label(
            card2,
            textvariable=self.last_snapshot_var,
            justify="left",
            bg="#0b111b",
            fg="#14f2b0",
            font=("Consolas", 12),
            wraplength=260,
            anchor="nw",
        ).pack(fill="both", expand=True, padx=12, pady=(0, 12))

        card3 = self._make_card(parent, "HINWEISE")
        hint = (
            "• Spiel im Fenster/Borderless starten\n"
            "• Fenstername muss zu layout.json passen\n"
            "• ESC beendet Debug-Fenster"
        )
        tk.Label(card3, text=hint, bg="#0b111b", fg="#d8dde7", font=("Bahnschrift", 11), justify="left").pack(
            fill="x", padx=12, pady=(0, 12)
        )

    def _entry_row(self, parent, label, variable, browse=False):
        row = tk.Frame(parent, bg="#0b111b")
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, width=18, anchor="w", bg="#0b111b", fg="#d8dde7", font=("Bahnschrift", 11)).pack(side="left")
        entry = tk.Entry(row, textvariable=variable, bg="#09101a", fg="#14f2b0", insertbackground="#14f2b0", relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        if browse:
            tk.Button(
                row,
                text="...",
                command=self.choose_layout,
                bg="#09101a",
                fg="#14f2b0",
                activebackground="#102236",
                activeforeground="#14f2b0",
                relief="flat",
                width=3,
            ).pack(side="left", padx=(8, 0))

    def _styled_check(self, parent, text, variable):
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            bg="#0b111b",
            fg="#d8dde7",
            activebackground="#0b111b",
            activeforeground="#14f2b0",
            selectcolor="#09101a",
            font=("Bahnschrift", 10),
        )

    def _neon_button(self, parent, text, command, color="#14f2b0"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#09101a",
            fg=color,
            activebackground="#102236",
            activeforeground=color,
            relief="flat",
            font=("Bahnschrift", 11, "bold"),
            padx=18,
            pady=8,
            cursor="hand2",
        )

    def choose_layout(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Alle Dateien", "*.*")])
        if path:
            self.layout_var.set(path)

    def build_command(self):
        cmd = [
            sys.executable,
            "main.py",
            "--layout",
            self.layout_var.get(),
            "--fps",
            self.fps_var.get(),
            "--snapshot-interval",
            self.snapshot_var.get(),
            "--db",
            "on" if self.db_var.get() else "off",
        ]
        if self.db_var.get():
            cmd += ["--db-path", self.db_path_var.get()]
        if self.debug_var.get():
            cmd.append("--debug")
        if self.debug_ocr_var.get():
            cmd.append("--debug-ocr")
        return cmd

    def start_process(self):
        if self.is_running:
            return

        layout_path = Path(self.layout_var.get())
        if not layout_path.exists():
            messagebox.showerror("Fehler", f"Layout nicht gefunden:\n{layout_path}")
            return

        cmd = self.build_command()
        self.log("Starte: " + " ".join(cmd))
        self.status_var.set("LÄUFT")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=Path(__file__).parent,
            )
        except Exception as exc:
            self.status_var.set("FEHLER")
            messagebox.showerror("Start fehlgeschlagen", str(exc))
            return

        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self._stream_output, daemon=True).start()

    def _stream_output(self):
        assert self.process and self.process.stdout
        for line in self.process.stdout:
            clean = line.rstrip()
            self.root.after(0, self.log, clean)
            self.root.after(0, self._consume_snapshot, clean)

        return_code = self.process.wait()
        self.root.after(0, self._on_process_end, return_code)

    def _consume_snapshot(self, line: str):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            if line.startswith("Nutze Fenster:"):
                self.window_title_var.set(line)
            return

        summary = [
            f"Session: {payload.get('session_seconds', 0):.0f}s",
            f"Profit/h: {payload.get('profit_per_hour', 0):,.0f}",
            f"Kills/min: {payload.get('kills_per_min', 0):.2f}",
            f"Runs/h: {payload.get('runs_per_hour', 0):.2f}",
        ]
        self.last_snapshot_var.set("\n".join(summary))

    def _on_process_end(self, return_code):
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if return_code == 0:
            self.status_var.set("GESTOPPT")
            self.log("Prozess sauber beendet.")
        else:
            self.status_var.set("FEHLER")
            self.log(f"Prozess beendet mit Code {return_code}.")

    def stop_process(self):
        if not self.process or not self.is_running:
            return
        self.log("Stoppe Analyse...")
        self.process.terminate()

    def on_close(self):
        if self.is_running and self.process:
            self.process.terminate()
        self.root.destroy()

    def log(self, text: str):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")


def main():
    root = tk.Tk()
    app = StartProgrammApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
