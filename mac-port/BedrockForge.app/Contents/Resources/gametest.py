import sys
import subprocess
import os
import shutil

# Try to import nbtlib, install if missing
try:
    import nbtlib
except ImportError:
    print("nbtlib not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nbtlib"])
    import nbtlib

from nbtlib import File, tag

def enable_gametest_in_world(world_path):
    level_dat_path = os.path.join(world_path, "level.dat")
    if not os.path.isfile(level_dat_path):
        print(f"level.dat not found in {world_path}, skipping.")
        return

    try:
        nbt_file = File.load(level_dat_path)
    except Exception as e:
        print(f"Failed to load NBT for {world_path}: {e}")
        return

    root = nbt_file

    # Enable GameTest and experimental gameplay
    root['Data']['GameTestEnabled'] = tag.Byte(1)
    root['Data']['ExperimentalGameplay'] = tag.Byte(1)

    nbt_file.save(level_dat_path)
    print(f"Enabled GameTest + ExperimentalGameplay in {world_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: enable_gametest.py <world_path>")
        sys.exit(1)

    world_path = sys.argv[1]
    enable_gametest_in_world(world_path)

if __name__ == "__main__":
    main()
