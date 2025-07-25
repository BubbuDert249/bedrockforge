# BedrockForge
Click "Specify Minecraft Bedrock Location" <br>
Add ```.bdr``` files to the ```mods``` folder <br>
Restart BedrockForge <br>
Click "Enable" to enable the mod, or "Disable" to disable it <br>
Minecraft Bedrock/EDU locations: <br>
Windows: <br>
Non-preview: <br>
```%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang``` <br>
Preview: <br>
```%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe_x64__8wekyb3d8bbwe\LocalState\games\com.mojang``` <br>
or <br>
```%LocalAppData%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang``` <br>
Mac: <br>
```~/Library/Application Support/minecrafteducationedition/games/com.mojang/``` <br>
<br>
# How to create a mod: <br>
1. Create a ```mods``` folder (if non-existent) in the app folder (or create a BedrockMods folder in ~ for Mac Port) <br>
2. Make a folder with any name inside ```mods``` <br>
3. Add inside it your behavior pack named ```behavior``` and resource pack named ```resource``` (as folders) <br>
4. Put a icon to the folder
5. Create a ```info.json``` <br>
```Info.json``` example: <br>
```
{
  "name": "My Mod",
  "version": "1.0.0",
  "creator": "You",
  "description": "Example BedrockForge mod.",
  "requires_minecraft": "1.21",
  "preview": false,
  "icon": "icon.png",
  "jsfile": ["main.js"]
}
```
name - Name of the mod <br>
version - Version of the mod <br>
creator - Person who created the mod <br>
description - Description of the mod <br>
requires_minecraft - The required Minecraft Bedrock version <br>
preview - Is the mod for Bedrock preview <br>
icon - Icon name for the mod icon <br>
jsfile - The file that  uses the JS API, can add more (like ["script1.js", "script2.js"] ) <br>
6. Add a ```.js``` file (one or more, value of jsfile in the JSON) using the Bedrock JavaScript API (required) <br>
7. Zip the contents of the folder <br>
8. Rename the ```.zip``` to ```.bdr``` <br>
9. Put the ```.bdr``` file directly in the root of the ```mods``` folder <br>
10. Run BedrockForge, click Enable on your mod <br>
# FOR DEVS: <br>
How the Windows port works? It runs on tkinter for GUI, PIL for mod icon and os,shutil for managing files and folders <br>
How the Mac port works? It runs on shell to run the uncompiled AppleScript and AppleScript for copying and Dialogs for GUI <br>
The Mac port was built on Windows <br>
The Mac port is for Edu Edition, because only Windows-based devices can run Bedrock, but ones that aren't (like Android or Mac) just have Edu <br>
