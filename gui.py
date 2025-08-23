#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PassForge GUI – Advanced Password Generator
Author: netR4ptOr@  (GitHub: networkblackhat569-jpg)
Email: networkblackhat5692@gmail.com
License: MIT

Features:
- Easy/Medium/Strong/Very Strong modes
- Custom length + include/exclude: UPPER/lower/digits/symbols
- Generate multiple passwords at once
- Scrollable list with per-password Copy button
- Copy All / Save to File / Clear
- Export to CSV (KeePass / Bitwarden style) & JSON
- Light/Dark theme toggle
- Window controls: Exit, Restore/Maximize lock (no minimize button shown)

Note:
- KeePass/Bitwarden import CSV formats vary by version. We export two common presets.
"""

import os
import sys
import json
import csv
import random
import string
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "PassForge"
AUTHOR = "netR4ptOr@"
AUTHOR_EMAIL = "networkblackhat5692@gmail.com"
GITHUB = "https://github.com/networkblackhat569-jpg/passforge"
VERSION = "1.1.0"

# -----------------------------
# Password generation helpers
# -----------------------------
SYMBOLS = "!@#$%^&*()_-+=[]{};:,.<>/?|~"

def charset_from_flags(use_upper, use_lower, use_digits, use_symbols):
    chars = ""
    if use_upper:  chars += string.ascii_uppercase
    if use_lower:  chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_symbols:chars += SYMBOLS
    return chars

def ensure_all_selected_types(length, use_upper, use_lower, use_digits, use_symbols):
    """Minimum safe length per selected character class."""
    min_required = sum([use_upper, use_lower, use_digits, use_symbols])
    return max(length, min_required if min_required > 0 else 1)

def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    chars = charset_from_flags(use_upper, use_lower, use_digits, use_symbols)
    if not chars:
        raise ValueError("Please select at least one character set.")
    length = ensure_all_selected_types(length, use_upper, use_lower, use_digits, use_symbols)

    # Guarantee at least one from each selected class
    parts = []
    if use_upper:  parts.append(random.choice(string.ascii_uppercase))
    if use_lower:  parts.append(random.choice(string.ascii_lowercase))
    if use_digits: parts.append(random.choice(string.digits))
    if use_symbols:parts.append(random.choice(SYMBOLS))

    remaining = length - len(parts)
    parts += [random.choice(chars) for _ in range(max(0, remaining))]
    random.shuffle(parts)
    return "".join(parts)

def generate_by_mode(mode, count):
    """Modes: Easy/Medium/Strong/Very Strong (preconfigured flags+length)"""
    presets = {
        "Easy":        {"length": 10, "upper": True,  "lower": True,  "digits": True,  "symbols": False},
        "Medium":      {"length": 12, "upper": True,  "lower": True,  "digits": True,  "symbols": True},
        "Strong":      {"length": 16, "upper": True,  "lower": True,  "digits": True,  "symbols": True},
        "Very Strong": {"length": 24, "upper": True,  "lower": True,  "digits": True,  "symbols": True},
    }
    p = presets.get(mode, presets["Strong"])
    return [
        generate_password(
            p["length"], p["upper"], p["lower"], p["digits"], p["symbols"]
        )
        for _ in range(count)
    ]

# -----------------------------
# GUI App
# -----------------------------
class PassForgeGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Basic Window
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("920x640")
        self.minsize(900, 620)

        # Hide minimize button by using overrideredirect-like titlebar? (Not cross-platform safe)
        # Safe approach: keep default titlebar but provide our top bar. We'll ignore minimize behavior.
        # Users asked "minimize button ko show mat kro": On most OS we can't hide it reliably.
        # Workaround: Disable <Unmap> (minimize) by re-map to normal.
        self.bind("<Unmap>", self._on_unmap)

        # Theme
        self.dark = True
        self._apply_theme()

        # Styles
        self.style = ttk.Style(self)
        self._config_styles()

        # Top branding bar
        self._build_titlebar()

        # Main content
        self._build_controls()
        self._build_output_panel()

        # Storage
        self.generated = []  # list of passwords
        self.selected_mode = tk.StringVar(value="Strong")

    # ---------- Title / Controls ----------
    def _build_titlebar(self):
        bar = ttk.Frame(self, padding=(12, 10))
        bar.pack(fill="x", side="top")

        title = ttk.Label(
            bar,
            text=f"🔐 {APP_NAME} – Advanced Password Generator",
            style="Title.TLabel"
        )
        title.pack(side="left")

        # Theme toggle
        theme_btn = ttk.Button(bar, text="🌗 Theme", command=self.toggle_theme)
        theme_btn.pack(side="right", padx=(6,0))
        # Exit button
        exit_btn = ttk.Button(bar, text="✖ Exit", command=self._exit_app)
        exit_btn.pack(side="right", padx=(6,0))
        # Restore button
        restore_btn = ttk.Button(bar, text="⤢ Restore", command=self._force_restore)
        restore_btn.pack(side="right", padx=(6,0))

    def _build_controls(self):
        outer = ttk.Frame(self, padding=(12, 8))
        outer.pack(fill="x", side="top")

        # Left: Mode & Count
        left = ttk.LabelFrame(outer, text="Quick Modes", padding=(12, 6))
        left.pack(side="left", padx=(0, 8), fill="x")

        mode_row = ttk.Frame(left)
        mode_row.pack(fill="x", pady=2)
        ttk.Label(mode_row, text="Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value="Strong")
        cb = ttk.Combobox(mode_row, textvariable=self.mode_var,
                          values=["Easy", "Medium", "Strong", "Very Strong"], width=14, state="readonly")
        cb.pack(side="left", padx=6)

        cnt_row = ttk.Frame(left)
        cnt_row.pack(fill="x", pady=2)
        ttk.Label(cnt_row, text="How many passwords?").pack(side="left")
        self.count_var = tk.IntVar(value=5)
        cnt = ttk.Spinbox(cnt_row, from_=1, to=100, textvariable=self.count_var, width=6)
        cnt.pack(side="left", padx=6)

        gen_mode_btn = ttk.Button(left, text="⚙️ Generate by Mode", command=self.on_generate_by_mode)
        gen_mode_btn.pack(pady=6, fill="x")

        # Middle: Custom Options
        mid = ttk.LabelFrame(outer, text="Custom Generation", padding=(12, 6))
        mid.pack(side="left", padx=8, fill="x")

        len_row = ttk.Frame(mid)
        len_row.pack(fill="x", pady=2)
        ttk.Label(len_row, text="Length:").pack(side="left")
        self.len_var = tk.IntVar(value=16)
        ln = ttk.Spinbox(len_row, from_=4, to=128, textvariable=self.len_var, width=6)
        ln.pack(side="left", padx=6)

        flags = ttk.Frame(mid)
        flags.pack(fill="x", pady=4)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        ttk.Checkbutton(flags, text="UPPER", variable=self.use_upper).pack(side="left", padx=4)
        ttk.Checkbutton(flags, text="lower", variable=self.use_lower).pack(side="left", padx=4)
        ttk.Checkbutton(flags, text="123", variable=self.use_digits).pack(side="left", padx=4)
        ttk.Checkbutton(flags, text="@#$", variable=self.use_symbols).pack(side="left", padx=4)

        cnt_row2 = ttk.Frame(mid)
        cnt_row2.pack(fill="x", pady=2)
        ttk.Label(cnt_row2, text="Count:").pack(side="left")
        self.count_custom_var = tk.IntVar(value=5)
        cnt2 = ttk.Spinbox(cnt_row2, from_=1, to=100, textvariable=self.count_custom_var, width=6)
        cnt2.pack(side="left", padx=6)

        gen_custom_btn = ttk.Button(mid, text="🎯 Generate (Custom)", command=self.on_generate_custom)
        gen_custom_btn.pack(pady=6, fill="x")

        # Right: Actions
        right = ttk.LabelFrame(outer, text="Actions", padding=(12, 6))
        right.pack(side="left", padx=(8,0), fill="x")

        ttk.Button(right, text="📋 Copy All", command=self.copy_all).pack(fill="x", pady=3)
        ttk.Button(right, text="💾 Save to File (txt)", command=self.save_to_file).pack(fill="x", pady=3)

        # Export submenu buttons
        ttk.Label(right, text="Export Passwords:").pack(anchor="w", pady=(8,2))
        ttk.Button(right, text="⬇ CSV – KeePass style", command=lambda: self.export_csv(style="keepass")).pack(fill="x", pady=2)
        ttk.Button(right, text="⬇ CSV – Bitwarden style", command=lambda: self.export_csv(style="bitwarden")).pack(fill="x", pady=2)
        ttk.Button(right, text="⬇ JSON", command=self.export_json).pack(fill="x", pady=2)

        ttk.Button(right, text="🧹 Clear List", command=self.clear_list).pack(fill="x", pady=(10,0))

    def _build_output_panel(self):
        wrapper = ttk.Frame(self, padding=(12, 8))
        wrapper.pack(fill="both", expand=True)

        # Header row
        hdr = ttk.Frame(wrapper)
        hdr.pack(fill="x", pady=(0,6))
        ttk.Label(hdr, text="Generated Passwords", style="Header.TLabel").pack(side="left")

        # Scrollable area
        container = ttk.Frame(wrapper)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0, bd=0,
                                background=self._bg(), relief="flat")
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        self.list_frame = ttk.Frame(self.canvas)
        self.list_frame_id = self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self._on_frame_configure())
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # ---------- Event Logic ----------
    def on_generate_by_mode(self):
        try:
            mode = self.mode_var.get()
            n = max(1, int(self.count_var.get()))
            pwds = generate_by_mode(mode, n)
            self._append_passwords(pwds)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def on_generate_custom(self):
        try:
            length = max(4, int(self.len_var.get()))
            n = max(1, int(self.count_custom_var.get()))
            pwds = [
                generate_password(
                    length,
                    self.use_upper.get(),
                    self.use_lower.get(),
                    self.use_digits.get(),
                    self.use_symbols.get()
                )
                for _ in range(n)
            ]
            self._append_passwords(pwds)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _append_passwords(self, pwds):
        for p in pwds:
            self.generated.append(p)
            self._add_row(p)

    def _add_row(self, pwd):
        row = ttk.Frame(self.list_frame)
        row.pack(fill="x", pady=3)

        # Password entry (readonly)
        var = tk.StringVar(value=pwd)
        ent = ttk.Entry(row, textvariable=var)
        ent.configure(state="readonly")
        ent.pack(side="left", fill="x", expand=True, padx=(0,6))

        ttk.Button(row, text="Copy", command=lambda v=pwd: self._copy_one(v)).pack(side="left", padx=2)

    def _copy_one(self, value):
        pyperclip.copy(value)
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def copy_all(self):
        if not self.generated:
            messagebox.showwarning("Empty", "No passwords to copy.")
            return
        pyperclip.copy("\n".join(self.generated))
        messagebox.showinfo("Copied", "All passwords copied to clipboard.")

    def save_to_file(self):
        if not self.generated:
            messagebox.showwarning("Empty", "No passwords to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save passwords",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.generated))
        messagebox.showinfo("Saved", f"Saved to:\n{path}")

    def export_csv(self, style="keepass"):
        if not self.generated:
            messagebox.showwarning("Empty", "No passwords to export.")
            return

        if style == "keepass":
            default_name = "passforge_keepass.csv"
            headers = ["Title", "Username", "Password", "URL", "Notes"]
            # Minimal data; users can edit after import
            def row(pw):
                return ["Generated", "", pw, "", "Generated by PassForge"]
        elif style == "bitwarden":
            default_name = "passforge_bitwarden.csv"
            # Common Bitwarden CSV columns (simplified)
            headers = ["name", "username", "password", "url", "notes"]
            def row(pw):
                return ["Generated", "", pw, "", "Generated by PassForge"]
        else:
            messagebox.showerror("Error", "Unknown CSV style.")
            return

        path = filedialog.asksaveasfilename(
            title="Export CSV",
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for pw in self.generated:
                writer.writerow(row(pw))

        messagebox.showinfo("Exported", f"CSV exported:\n{path}\n\nImport this file in your password manager.")

    def export_json(self):
        if not self.generated:
            messagebox.showwarning("Empty", "No passwords to export.")
            return

        path = filedialog.asksaveasfilename(
            title="Export JSON",
            initialfile="passforge_passwords.json",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not path:
            return

        data = {
            "app": APP_NAME,
            "version": VERSION,
            "author": AUTHOR,
            "generated": self.generated
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Exported", f"JSON exported:\n{path}")

    def clear_list(self):
        if not self.generated:
            return
        if not messagebox.askyesno("Confirm", "Clear all generated passwords from the list?"):
            return
        self.generated.clear()
        for child in list(self.list_frame.children.values()):
            child.destroy()

    # ---------- Theme / Window ----------
    def toggle_theme(self):
        self.dark = not self.dark
        self._apply_theme()
        self._config_styles()
        # Refresh canvas bg
        self.canvas.configure(background=self._bg())

    def _apply_theme(self):
        if self.dark:
            self.configure(bg="#0f1220")
        else:
            self.configure(bg="#f5f6fb")

    def _config_styles(self):
        bg = self._bg()
        fg = self._fg()
        acc = self._accent()

        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), background=bg, foreground=acc)
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background=bg, foreground=fg)
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)

    def _bg(self):
        return "#0f1220" if self.dark else "#ffffff"

    def _fg(self):
        return "#e9ecf1" if self.dark else "#1c1f2a"

    def _accent(self):
        return "#7aa2f7" if self.dark else "#2f59ff"

    def _on_frame_configure(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Make inner frame resize to canvas width
        self.canvas.itemconfigure(self.list_frame_id, width=event.width)

    def _force_restore(self):
        try:
            self.state("normal")
            self.deiconify()
        except Exception:
            pass

    def _on_unmap(self, event):
        # Prevent minimize (re-show the window)
        try:
            if self.state() == "iconic":
                self.after(50, self.deiconify)
        except Exception:
            pass

    def _exit_app(self):
        if messagebox.askokcancel("Exit", "Close the application?"):
            self.destroy()

def main():
    app = PassForgeGUI()
    app.mainloop()

if __name__ == "__main__":
    main()

