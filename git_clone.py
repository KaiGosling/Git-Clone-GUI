import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys
import shutil


BG        = "#080810"
CARD_BG   = "#0c0c1c"
CARD_BD   = "#141428"
CYAN      = "#00e5ff"
WHITE     = "#ffffff"
DIM       = "#282840"
DIMMER    = "#1e1e36"
DIMMOST   = "#101018"
RED       = "#ff3366"
INPUT_BG  = "#040408"
INPUT_BD  = "#0e0e1c"
LAUNCH_BG = "#001418"
FONT      = "Courier New"


class GitCloneApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Git Clone")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.geometry("440x560")
        self._clone_thread = None
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        r = self.root

        # ── Header ──────────────────────────────────────────────────────────
        hf = tk.Frame(r, bg=BG)
        hf.pack(fill=tk.X, padx=24, pady=(24, 2))
        tk.Label(hf, text="GIT",    font=(FONT, 30, "bold"), fg=CYAN,  bg=BG).pack(side=tk.LEFT)
        tk.Label(hf, text=" CLONE", font=(FONT, 30, "bold"), fg=WHITE, bg=BG).pack(side=tk.LEFT)
        tk.Label(r, text="quick clone  \u00b7  paste url  \u00b7  set destination",
                 font=(FONT, 9), fg=WHITE, bg=BG).pack(anchor=tk.W, padx=26)
        tk.Frame(r, bg=CARD_BD, height=1).pack(fill=tk.X, padx=22, pady=14)

        # ── Repo URL card ───────────────────────────────────────────────────
        url_card = tk.Frame(r, bg=CARD_BG, highlightbackground=CARD_BD, highlightthickness=1)
        url_card.pack(fill=tk.X, padx=22, pady=(0, 10))

        url_hdr = tk.Frame(url_card, bg=CARD_BG)
        url_hdr.pack(fill=tk.X, padx=14, pady=(8, 2))
        tk.Label(url_hdr, text="REPOSITORY URL (Paste repository URL here) :", font=(FONT, 8, "bold"),
                 fg=WHITE, bg=CARD_BG).pack(side=tk.LEFT)

        url_body = tk.Frame(url_card, bg=CARD_BG)
        url_body.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.repo_var = tk.StringVar()
        self.repo_var.trace_add("write", self._update_preview)
        self.repo_entry = tk.Entry(
            url_body, textvariable=self.repo_var,
            font=(FONT, 9), fg=CYAN, bg=INPUT_BG,
            insertbackground=CYAN, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=INPUT_BD,
            highlightcolor=CYAN
        )
        self.repo_entry.insert(0, " ")
        self.repo_entry.pack(fill=tk.X)

        # ── Destination card ────────────────────────────────────────────────
        dest_card = tk.Frame(r, bg=CARD_BG, highlightbackground=CARD_BD, highlightthickness=1)
        dest_card.pack(fill=tk.X, padx=22, pady=(0, 10))

        dest_hdr = tk.Frame(dest_card, bg=CARD_BG)
        dest_hdr.pack(fill=tk.X, padx=14, pady=(8, 2))
        tk.Label(dest_hdr, text="DESTINATION PATH", font=(FONT, 8, "bold"),
                 fg=WHITE, bg=CARD_BG).pack(side=tk.LEFT)
        self.browse_btn = tk.Button(
            dest_hdr, text="↗  browse", font=(FONT, 8),
            fg=WHITE, bg=CARD_BG,
            activeforeground=WHITE, activebackground=CARD_BG,
            relief=tk.FLAT,
            highlightbackground=CARD_BD, highlightthickness=1,
            cursor="hand2", padx=8, pady=2,
            command=self._browse
        )
        self.browse_btn.pack(side=tk.RIGHT)
        self.browse_btn.bind("<Enter>", lambda e: self.browse_btn.config(fg=BG, highlightbackground=CYAN, bg=CYAN))
        self.browse_btn.bind("<Leave>", lambda e: self.browse_btn.config(fg=WHITE, highlightbackground=CARD_BD, bg=CARD_BG))

        dest_body = tk.Frame(dest_card, bg=CARD_BG)
        dest_body.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.dest_var = tk.StringVar()
        self.dest_var.trace_add("write", self._update_preview)
        self.dest_entry = tk.Entry(
            dest_body, textvariable=self.dest_var,
            font=(FONT, 9), fg=CYAN, bg=INPUT_BG,
            insertbackground=CYAN, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=INPUT_BD,
            highlightcolor=CYAN
        )
        default_dest = os.path.join(os.path.expanduser("~"), "Desktop")
        self.dest_entry.insert(0, default_dest)
        self.dest_entry.pack(fill=tk.X)

        # ── Command preview ─────────────────────────────────────────────────
        prev_frame = tk.Frame(r, bg=INPUT_BG, highlightbackground=INPUT_BD, highlightthickness=1)
        prev_frame.pack(fill=tk.X, padx=22, pady=(0, 10))
        self.preview_lbl = tk.Label(
            prev_frame, text="git clone <repo-url> <destination>",
            font=(FONT, 8), fg=WHITE, bg=INPUT_BG,
            anchor=tk.W, padx=10, pady=6, wraplength=380, justify=tk.LEFT
        )
        self.preview_lbl.pack(fill=tk.X)

        # ── Buttons ─────────────────────────────────────────────────────────
        btn_row = tk.Frame(r, bg=BG)
        btn_row.pack(fill=tk.X, padx=22, pady=(0, 6))

        self.clone_btn = tk.Button(
            btn_row, text="\u25b6   CLONE REPOSITORY",
            font=(FONT, 11, "bold"),
            fg=CYAN, bg=LAUNCH_BG,
            activeforeground=WHITE, activebackground="#001e28",
            height=2, borderwidth=0, cursor="hand2",
            command=self._start_clone
        )
        self.clone_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.cancel_btn = tk.Button(
            btn_row, text="\u2715  cancel",
            font=(FONT, 9),
            fg=WHITE, bg=BG,
            activeforeground=WHITE, activebackground=BG,
            borderwidth=1, relief=tk.FLAT,
            highlightbackground=CARD_BD, highlightthickness=1,
            cursor="hand2",
            command=self._cancel
        )
        self.cancel_btn.pack(side=tk.LEFT, ipadx=10, ipady=6)
        self.cancel_btn.bind("<Enter>", lambda e: self.cancel_btn.config(fg=BG, highlightbackground=CYAN, bg=CYAN))
        self.cancel_btn.bind("<Leave>", lambda e: self.cancel_btn.config(fg=WHITE, highlightbackground=CARD_BD, bg=BG))

        # ── Status ──────────────────────────────────────────────────────────
        status_row = tk.Frame(r, bg=BG)
        status_row.pack(fill=tk.X, padx=24, pady=(4, 0))
        self.dot_lbl = tk.Label(status_row, text="\u25cf", font=(FONT, 11),
                                fg=CYAN, bg=BG)
        self.dot_lbl.pack(side=tk.LEFT)
        self.status_lbl = tk.Label(status_row, text=" Ready.",
                                   font=(FONT, 8), fg=CYAN, bg=BG)
        self.status_lbl.pack(side=tk.LEFT)

        # ── Footer ──────────────────────────────────────────────────────────
        tk.Label(r, text="git clone tool  \u00b7  vr cinema suite  \u00b7  kairu kumaneko",
                 font=(FONT, 7), fg=DIMMOST, bg=BG).pack(side=tk.BOTTOM, pady=(0, 2))
        self.support_btn = tk.Button(
            r, text="\u2665  SUPPORT THE DEVELOPER",
            font=(FONT, 8), fg=RED, bg=BG,
            activeforeground=WHITE, activebackground="#1a0010",
            borderwidth=0, cursor="hand2",
            command=self._show_donation
        )
        self.support_btn.pack(side=tk.BOTTOM, pady=(0, 4))
        self.support_btn.bind("<Enter>", lambda e: self.support_btn.config(fg=WHITE, bg="#1a0010"))
        self.support_btn.bind("<Leave>", lambda e: self.support_btn.config(fg=RED, bg=BG))

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _update_preview(self, *_):
        repo = self.repo_var.get().strip() or "<repo-url>"
        dest = self.dest_var.get().strip() or "<destination>"
        self.preview_lbl.config(text=f'git clone {repo} "{dest}"')

    def _browse(self):
        path = filedialog.askdirectory(title="Select destination folder")
        if path:
            self.dest_var.set(path)

    def _set_status(self, dot_color, msg, msg_color=None):
        self.dot_lbl.config(fg=dot_color)
        self.status_lbl.config(text=f" {msg}", fg=msg_color or dot_color)

    def _cancel(self):
        self.repo_var.set("")
        self.dest_var.set("")
        self._set_status(DIMMER, "Ready.", DIMMER)
        self.repo_entry.focus()

    # ── Clone logic ─────────────────────────────────────────────────────────

    def _start_clone(self):
        repo = self.repo_var.get().strip()
        dest = self.dest_var.get().strip()

        if not repo:
            self._set_status(RED, "Enter a repository URL.", RED)
            self.repo_entry.focus()
            return
        if not (repo.startswith("http") or repo.startswith("git@")):
            self._set_status(RED, "URL should start with https:// or git@", RED)
            self.repo_entry.focus()
            return
        if not dest:
            self._set_status(RED, "Enter a destination path.", RED)
            self.dest_entry.focus()
            return

        if not shutil.which("git"):
            messagebox.showerror(
                "Git not found",
                "git is not installed or not in PATH.\n\nDownload from: https://git-scm.com"
            )
            return

        self.clone_btn.config(state=tk.DISABLED, text="\u25a0   CLONING...", fg=DIM)
        self._set_status(CYAN, "Cloning...", CYAN)
        self._clone_thread = threading.Thread(
            target=self._run_clone, args=(repo, dest), daemon=True
        )
        self._clone_thread.start()

    def _run_clone(self, repo: str, dest: str):
        try:
            # Always clone INTO a subfolder named after the repo
            # e.g. Desktop -> Desktop\Team-4
            repo_name = repo.rstrip("/").split("/")[-1].replace(".git", "") or "repo"
            final_dest = os.path.join(dest, repo_name)

            # If that subfolder already exists, append a number  (Team-4, Team-4-1, Team-4-2 ...)
            if os.path.exists(final_dest):
                counter = 1
                while os.path.exists(f"{final_dest}-{counter}"):
                    counter += 1
                final_dest = f"{final_dest}-{counter}"

            os.makedirs(dest, exist_ok=True)
            result = subprocess.run(
                ["git", "clone", repo, final_dest],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.root.after(0, self._on_success, repo_name, final_dest)
            else:
                err = (result.stderr or result.stdout or "Unknown error").strip()
                self.root.after(0, self._on_error, err)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_success(self, repo_name: str, dest: str):
        self.clone_btn.config(state=tk.NORMAL, text="\u25b6   CLONE REPOSITORY", fg=CYAN)
        self._set_status(CYAN, f"\u2713  {repo_name} cloned to {dest}", CYAN)
        messagebox.showinfo(
            "Clone complete",
            f"✓ Repository cloned successfully!\n\nDestination:\n{dest}"
        )

    def _on_error(self, err: str):
        self.clone_btn.config(state=tk.NORMAL, text="\u25b6   CLONE REPOSITORY", fg=CYAN)
        self._set_status(RED, f"Error: {err[:80]}", RED)
        messagebox.showerror("Clone failed", f"git clone failed:\n\n{err}")


    def _show_donation(self):
        win = tk.Toplevel(self.root)
        win.title("Support Kairu Kumaneko")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        self.root.update_idletasks()
        px = self.root.winfo_x() + self.root.winfo_width() // 2
        py = self.root.winfo_y() + self.root.winfo_height() // 2
        win.geometry(f"360x560+{px - 180}+{py - 280}")
        tk.Button(win, text="\u2715", font=(FONT, 10, "bold"),
                  fg="#333355", bg=BG, activeforeground=RED,
                  activebackground=BG, borderwidth=0, cursor="hand2",
                  command=win.destroy).place(relx=1.0, x=-14, y=10, anchor=tk.NE)
        hf = tk.Frame(win, bg=BG)
        hf.pack(pady=(28, 4))
        tk.Label(hf, text="SUPPORT DEVELOPER", font=(FONT, 18, "bold"),
                 fg=CYAN, bg=BG).pack(side=tk.LEFT)
        tk.Label(win, text="Kairu Kumaneko",
                 font=(FONT, 13, "bold"), fg=WHITE, bg=BG).pack()
        tk.Frame(win, bg=CARD_BD, height=1).pack(fill=tk.X, padx=24, pady=10)
        msg = (
            "I'm a digital artist and a beginner\n"
            "programmer. Please support me and\n"
            "thank you for using this program!\n\n"
            "If you'd like to donate, scan the QR\n"
            "below \u2014 any amount is appreciated. \u2665"
        )
        tk.Label(win, text=msg, font=(FONT, 9), fg="#FFFFFF",
                 bg=BG, justify=tk.CENTER).pack(padx=20)
        tk.Frame(win, bg=CARD_BD, height=1).pack(fill=tk.X, padx=24, pady=10)
        try:
            from PIL import Image, ImageTk
            if getattr(sys, "frozen", False):
                base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(base_dir, "assets")
            qr_path = os.path.join(assets_dir, "gcash-qr.png")
            img = Image.open(qr_path).convert("RGB")
            img = img.resize((200, 200), Image.LANCZOS)
            bordered = Image.new("RGB", (208, 208), (0, 229, 255))
            bordered.paste(img, (4, 4))
            tk_img = ImageTk.PhotoImage(bordered)
            lbl = tk.Label(win, image=tk_img, bg=BG)
            lbl.image = tk_img
            lbl.pack(pady=(0, 6))
        except Exception:
            tk.Label(win, text="[ QR code ]\n(place gcash-qr.png in assets/ folder)",
                     font=(FONT, 9), fg="#FFFFFF", bg=BG).pack(pady=20)
        tk.Label(win, text="GCash  \u00b7  InstaPay",
                 font=(FONT, 8), fg=WHITE, bg=BG).pack()
        tk.Label(win, text="Thank you very much! \U0001f64f",
                 font=(FONT, 9, "bold"), fg=CYAN, bg=BG).pack(pady=(8, 16))

    def _log(self, msg):
        try:
            self.log_var.set(f"\u203a {msg}")
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    try:
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        # Try .ico first, then fall back to .png via PIL
        ico_path = os.path.join(assets_dir, "icon.ico")
        png_path = os.path.join(assets_dir, "icon.png")
        if os.path.exists(ico_path):
            root.iconbitmap(ico_path)
        elif os.path.exists(png_path):
            from PIL import Image, ImageTk
            img = Image.open(png_path)
            icon = ImageTk.PhotoImage(img)
            root.iconphoto(True, icon)
    except Exception:
        pass
    app = GitCloneApp(root)
    root.mainloop()