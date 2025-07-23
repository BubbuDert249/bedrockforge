# BedrockForge
Click "Specify Minecraft Bedrock Location" <br>
Add ```.bdr``` files to the ```mods``` folder <br>
Restart BedrockForge <br>
Click "Enable" to enable the mod, or "Disable" to disable it <br>
<br>
# How to create a mod: <br>
1. Create a ```mods``` folder (if non-existent) in the app folder <br>
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
  "icon": icon.png
}
```
name - Name of the mod <br>
version - Version of the mod <br>
creator - Person who created the mod <br>
description - Description of the mod <br>
requires_minecraft - The required Minecraft Bedrock version <br>
preview - Is the mod for Bedrock preview <br>
icon - Icon name for the mod icon <br>
6. Zip the contents of the folder <br>
7. Rename the ```.zip``` to ```.bdr``` <br>
8. Put the ```.bdr``` file directly in the root of the ```mods``` folder <br>
9. Run BedrockForge, click Enable on your mod <br>
