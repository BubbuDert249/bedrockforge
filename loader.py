import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import shutil
import zipfile
import tempfile
import sys

DATA_FILE = "data.json"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BedrockForge")
        self.root.geometry("800x600")
        self.root.iconbitmap(resource_path("icon.ico"))

        self.minecraft_path = tk.StringVar()
        self.mod_states = {}

        self.load_data_file()

        tk.Label(root, text="BedrockForge", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(root, textvariable=self.minecraft_path, fg="blue").pack()
        tk.Button(root, text="Specify Minecraft Bedrock Location", command=self.select_minecraft_path).pack(pady=5)

        self.mods_frame = tk.Frame(root)
        self.mods_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_mods()

    def load_data_file(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.minecraft_path.set(data.get("minecraft_path", "(Path not set)"))
                    self.mod_states = data.get("mod_states", {})
            except json.JSONDecodeError:
                self.minecraft_path.set("(Path not set)")
                self.mod_states = {}
        else:
            self.minecraft_path.set("(Path not set)")
            self.mod_states = {}

    def save_data_file(self):
        data = {
            "minecraft_path": self.minecraft_path.get(),
            "mod_states": self.mod_states
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def select_minecraft_path(self):
        selected = filedialog.askdirectory(title="Select Minecraft Bedrock Folder")
        if selected:
            self.minecraft_path.set(selected)
            self.save_data_file()
            messagebox.showinfo("Path Saved", f"Minecraft Bedrock folder set to:\n{selected}")

    def load_mods(self):
        for widget in self.mods_frame.winfo_children():
            widget.destroy()

        mods_dir = os.path.join(os.getcwd(), "mods")
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)

        for mod_file in os.listdir(mods_dir):
            if mod_file.lower().endswith(".bdr"):
                mod_path = os.path.join(mods_dir, mod_file)
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        with zipfile.ZipFile(mod_path, 'r') as zip_ref:
                            zip_ref.extractall(tmpdir)
                            info_path = os.path.join(tmpdir, "info.json")
                            if os.path.isfile(info_path):
                                with open(info_path, "r") as f:
                                    info = json.load(f)
                                    self.add_mod_entry(mod_file, info, tmpdir)
                    except Exception as e:
                        print(f"Failed to load mod {mod_file}: {e}")

    def add_mod_entry(self, mod_file, info, temp_dir):
        frame = tk.Frame(self.mods_frame, borderwidth=1, relief="solid", padx=10, pady=5)
        frame.pack(fill="x", pady=5)

        name = info.get("name", mod_file)
        version = info.get("version", "Unknown")
        author = info.get("creator", "Unknown")
        description = info.get("description", "No description provided.")
        required_version = info.get("requires_minecraft", "Any")
        preview = info.get("preview", False)
        icon_rel_path = info.get("icon")

        version_text = f"Designed for Bedrock {required_version}"
        if preview:
            version_text += " Preview"

        if icon_rel_path:
            icon_path = os.path.join(temp_dir, icon_rel_path)
            try:
                try:
                    resample_method = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_method = Image.LANCZOS
                image = Image.open(icon_path).resize((64, 64), resample_method)
                icon = ImageTk.PhotoImage(image)
                icon_label = tk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side="left", padx=5)
            except Exception as e:
                print(f"Failed to load icon '{icon_rel_path}' for mod {mod_file}: {e}")

        text_frame = tk.Frame(frame)
        text_frame.pack(side="left", fill="both", expand=True)

        tk.Label(text_frame, text=f"{name} v{version} by {author}", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(text_frame, text=description, wraplength=600, justify="left", fg="gray").pack(anchor="w", padx=5)
        tk.Label(text_frame, text=version_text, fg="blue").pack(anchor="w", padx=5)

        mod_name = os.path.splitext(mod_file)[0]
        enabled = self.mod_states.get(mod_name, False)

        toggle_button = tk.Button(frame, text="Disable" if enabled else "Enable", width=10)
        toggle_button.pack(side="right", padx=5)
        toggle_button.config(command=lambda b=toggle_button, m=mod_file: self.toggle_mod(b, m))

    def toggle_mod(self, button, mod_file):
        mod_name = os.path.splitext(mod_file)[0]
        current_state = self.mod_states.get(mod_name, False)
        new_state = not current_state
        self.mod_states[mod_name] = new_state
        button["text"] = "Disable" if new_state else "Enable"
        self.save_data_file()

        if self.minecraft_path.get() == "(Path not set)":
            messagebox.showerror("Error", "Minecraft Bedrock path not set!")
            return

        base_path = self.minecraft_path.get()
        dev_behavior_dir = os.path.join(base_path, "behavior_packs")
        dev_resource_dir = os.path.join(base_path, "resource_packs")
        display_name = mod_name or mod_file

        os.makedirs(dev_behavior_dir, exist_ok=True)
        os.makedirs(dev_resource_dir, exist_ok=True)

        mods_dir = os.path.join(os.getcwd(), "mods")
        mod_path = os.path.join(mods_dir, mod_file)

        behavior_dst = os.path.join(dev_behavior_dir, mod_name + "_behavior")
        resource_dst = os.path.join(dev_resource_dir, mod_name + "_resource")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with zipfile.ZipFile(mod_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)

                info_path = os.path.join(tmpdir, "info.json")
                if not os.path.isfile(info_path):
                    messagebox.showerror("Missing Info", f"The mod '{display_name}' is missing info.json.")
                    return

                with open(info_path, "r") as f:
                    info = json.load(f)

                jsfiles = info.get("jsfile")
                if not jsfiles:
                    messagebox.showerror(
                        "Missing JavaScript File",
                        f"The mod '{display_name}' is missing the 'jsfile' entry in info.json."
                    )
                    return

                if isinstance(jsfiles, str):
                    jsfiles = [jsfiles]

                for jsfile in jsfiles:
                    js_src = os.path.join(tmpdir, jsfile)
                    if not os.path.isfile(js_src):
                        messagebox.showerror("Missing Script", f"Mod '{display_name}' is missing required JS file: {jsfile}")
                        return

                behavior_src = os.path.join(tmpdir, "behavior")
                resource_src = os.path.join(tmpdir, "resource")

                if new_state:
                    if os.path.exists(behavior_dst):
                        shutil.rmtree(behavior_dst)
                    if os.path.exists(resource_dst):
                        shutil.rmtree(resource_dst)

                    shutil.copytree(behavior_src, behavior_dst)
                    shutil.copytree(resource_src, resource_dst)

                    scripts_dst_dir = os.path.join(behavior_dst, "scripts")
                    os.makedirs(scripts_dst_dir, exist_ok=True)
                    for jsfile in jsfiles:
                        js_src = os.path.join(tmpdir, jsfile)
                        shutil.copy2(js_src, os.path.join(scripts_dst_dir, os.path.basename(jsfile)))
                else:
                    if os.path.exists(behavior_dst):
                        shutil.rmtree(behavior_dst)
                    if os.path.exists(resource_dst):
                        shutil.rmtree(resource_dst)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to {'enable' if new_state else 'disable'} mod {mod_file}:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModManagerApp(root)
    root.mainloop()
