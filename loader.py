import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil

DATA_FILE = "data.json"

class ModManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BedrockForge")
        self.root.geometry("800x600")
        self.root.iconbitmap("icon.ico")

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

        for mod_folder in os.listdir(mods_dir):
            mod_path = os.path.join(mods_dir, mod_folder)
            behavior_path = os.path.join(mod_path, "behavior")
            resource_path = os.path.join(mod_path, "resource")
            info_path = os.path.join(mod_path, "info.json")

            if os.path.isdir(mod_path) and os.path.isfile(info_path):
                if os.path.isdir(behavior_path) and os.path.isdir(resource_path):
                    try:
                        with open(info_path, "r") as f:
                            info = json.load(f)
                            self.add_mod_entry(mod_folder, info)
                    except json.JSONDecodeError:
                        continue

    def add_mod_entry(self, mod_folder, info):
        frame = tk.Frame(self.mods_frame, borderwidth=1, relief="solid", padx=10, pady=5)
        frame.pack(fill="x", pady=5)

        name = info.get("name", mod_folder)
        version = info.get("version", "Unknown")
        author = info.get("creator", "Unknown")
        description = info.get("description", "No description provided.")
        required_version = info.get("requires_minecraft", "Any")
        preview = info.get("preview", False)

        # Main title
        version_text = f"Designed for Bedrock {required_version}"
        if preview:
            version_text += " Preview"
        
        # Description
        tk.Label(frame, text=f"{name} v{version} by {author}", font=("Arial", 12, "bold")).pack(anchor="w")

        # Required Minecraft version
        tk.Label(frame,text=description, wraplength=600, justify="left", fg="gray").pack(anchor="w", padx=5)

        tk.Label(frame, text=version_text, fg="blue").pack(anchor="w", padx=5)

        enabled = self.mod_states.get(mod_folder, False)

        toggle_button = tk.Button(frame, text="Disable" if enabled else "Enable", width=10)
        toggle_button.pack(side="right", padx=5)
        toggle_button.config(command=lambda b=toggle_button, m=mod_folder: self.toggle_mod(b, m))

    def toggle_mod(self, button, mod_folder):
        current_state = self.mod_states.get(mod_folder, False)
        new_state = not current_state
        self.mod_states[mod_folder] = new_state
        button["text"] = "Disable" if new_state else "Enable"
        self.save_data_file()

        if self.minecraft_path.get() == "(Path not set)":
            messagebox.showerror("Error", "Minecraft Bedrock path not set!")
            return

        base_path = self.minecraft_path.get()
        dev_behavior_dir = os.path.join(base_path, "behavior_packs")
        dev_resource_dir = os.path.join(base_path, "resource_packs")

        os.makedirs(dev_behavior_dir, exist_ok=True)
        os.makedirs(dev_resource_dir, exist_ok=True)

        mods_dir = os.path.join(os.getcwd(), "mods")
        mod_path = os.path.join(mods_dir, mod_folder)

        behavior_src = os.path.join(mod_path, "behavior")
        resource_src = os.path.join(mod_path, "resource")

        behavior_dst = os.path.join(dev_behavior_dir, mod_folder + "_behavior")
        resource_dst = os.path.join(dev_resource_dir, mod_folder + "_resource")

        if new_state:
            try:
                if os.path.exists(behavior_dst):
                    shutil.rmtree(behavior_dst)
                if os.path.exists(resource_dst):
                    shutil.rmtree(resource_dst)
                shutil.copytree(behavior_src, behavior_dst)
                shutil.copytree(resource_src, resource_dst)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to enable mod {mod_folder}:\n{e}")
        else:
            try:
                if os.path.exists(behavior_dst):
                    shutil.rmtree(behavior_dst)
                if os.path.exists(resource_dst):
                    shutil.rmtree(resource_dst)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to disable mod {mod_folder}:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModManagerApp(root)
    root.mainloop()
