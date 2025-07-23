property modsFolderPath : (POSIX path of (path to home folder)) & "BedrockMods/" -- folder where .bdr mods are stored
property minecraftEduPathFile : (POSIX path of (path to home folder)) & "bedrockforge_mc_path.txt"

-- Helper: read file contents as text
on readFile(thePath)
	try
		set theFile to open for access thePath
		set theContents to read theFile
		close access theFile
		return theContents
	on error
		try
			close access thePath
		end try
		return ""
	end try
end readFile

-- Helper: simple JSON parser for limited keys we want (name, version, description, requires_minecraft, preview, jsfile, icon)
on parseInfoJSON(jsonText)
	set infoDict to {}
	
	-- remove whitespace & newlines for simpler parsing
	set jsonText to do shell script "echo " & quoted form of jsonText & " | tr -d '\\n\\r '"
	
	-- Helper to extract string between "key":"value"
	on extractValue(key, text)
		try
			set AppleScript's text item delimiters to ("\"" & key & "\":")
			set parts to text items of text
			if (count of parts) < 2 then return ""
			set rest to item 2 of parts
			set AppleScript's text item delimiters to {"," , "}"} -- to catch value ends
			set valParts to text items of rest
			set valRaw to item 1 of valParts
			set AppleScript's text item delimiters to {"\"", "'"}
			set val to text items of valRaw
			if (count of val) < 2 then return valRaw
			return item 2 of val
		on error
			return ""
		end try
	end extractValue
	
	set infoDict's name to extractValue("name", jsonText)
	set infoDict's version to extractValue("version", jsonText)
	set infoDict's description to extractValue("description", jsonText)
	set infoDict's requires_minecraft to extractValue("requires_minecraft", jsonText)
	
	-- Extract preview boolean (true/false)
	try
		if jsonText contains "\"preview\":true" then
			set infoDict's preview to true
		else
			set infoDict's preview to false
		end if
	on error
		set infoDict's preview to false
	end try
	
	-- Extract icon filename
	set iconVal to extractValue("icon", jsonText)
	if iconVal is not "" then
		set infoDict's icon to iconVal
	else
		set infoDict's icon to ""
	end if
	
	-- Extract jsfile array (["file1.js","file2.js"]) as list
	try
		set AppleScript's text item delimiters to "\"jsfile\":"
		set jsParts to text items of jsonText
		if (count of jsParts) > 1 then
			set afterJS to item 2 of jsParts
			-- get text between [ and ]
			set AppleScript's text item delimiters to {"[", "]"}
			set arrParts to text items of afterJS
			if (count of arrParts) > 2 then
				set jsArrayRaw to item 2 of arrParts
				-- split by commas, remove quotes
				set AppleScript's text item delimiters to ","
				set jsFilesRaw to text items of jsArrayRaw
				set jsFiles to {}
				repeat with f in jsFilesRaw
					set fTrim to f
					set AppleScript's text item delimiters to {"\""}
					set fTrim to text items of fTrim
					if (count of fTrim) > 1 then
						set end of jsFiles to item 2 of fTrim
					end if
				end repeat
				set infoDict's jsfile to jsFiles
			else
				set infoDict's jsfile to {}
			end if
		else
			set infoDict's jsfile to {}
		end if
	on error
		set infoDict's jsfile to {}
	end try
	
	return infoDict
end parseInfoJSON

-- Prompt user for Minecraft EDU path or read saved path
on getMinecraftEduPath()
	try
		set savedPath to readFile(minecraftEduPathFile)
		if savedPath is not "" and (do shell script "test -d " & quoted form of savedPath & " && echo YES || echo NO") = "YES" then
			return savedPath
		end if
	on error
	end try
	
	set chosenPath to POSIX path of (choose folder with prompt "Select your Minecraft Education Edition game folder:")
	
	-- Save for next runs
	try
		set theFile to open for access file minecraftEduPathFile with write permission
		set eof of theFile to 0
		write chosenPath to theFile
		close access theFile
	on error
		try
			close access file minecraftEduPathFile
		end try
	end try
	
	return chosenPath
end getMinecraftEduPath

-- Copy folder contents from source to dest, create dest if missing
on copyFolderContents(src, dest)
	do shell script "mkdir -p " & quoted form of dest
	do shell script "cp -R " & quoted form of (src & "/.") & " " & quoted form of dest
end copyFolderContents

-- Delete folder (if exists)
on deleteFolder(folderPath)
	try
		do shell script "rm -rf " & quoted form of folderPath
	end try
end deleteFolder

-- Process mod: unzip to /tmp, read info.json, then delete temp unzip
on processMod(bdrPath)
	set tmpUnzipFolder to "/tmp/bedrockforge_temp_unzip_" & (do shell script "date +%s%N")
	do shell script "rm -rf " & quoted form of tmpUnzipFolder
	do shell script "mkdir -p " & quoted form of tmpUnzipFolder
	do shell script "unzip -qq " & quoted form of bdrPath & " -d " & quoted form of tmpUnzipFolder
	
	-- Read info.json inside unzip folder
	set infoJSONPath to tmpUnzipFolder & "/info.json"
	set jsonText to readFile(infoJSONPath)
	
	set modInfo to parseInfoJSON(jsonText)
	set modInfo's tmpFolder to tmpUnzipFolder
	set modInfo's bdrPath to bdrPath
	
	return modInfo
end processMod

-- Enable mod: copy behavior/ resource/ and jsfile(s)
on enableMod(modInfo, mcPath)
	set behaviorSrc to modInfo's tmpFolder & "/behavior"
	set resourceSrc to modInfo's tmpFolder & "/resource"
	set behaviorDest to mcPath & "/behavior_packs/" & modInfo's name
	set resourceDest to mcPath & "/resource_packs/" & modInfo's name
	
	-- Copy behavior folder
	if (do shell script "test -d " & quoted form of behaviorSrc & " && echo YES || echo NO") = "YES" then
		copyFolderContents(behaviorSrc, behaviorDest)
	end if
	
	-- Copy resource folder
	if (do shell script "test -d " & quoted form of resourceSrc & " && echo YES || echo NO") = "YES" then
		copyFolderContents(resourceSrc, resourceDest)
	end if
	
	-- Copy JS files to behavior/scripts
	if modInfo's jsfile is not {} then
		set scriptsDest to behaviorDest & "/scripts"
		do shell script "mkdir -p " & quoted form of scriptsDest
		repeat with jsFile in modInfo's jsfile
			set jsSrc to modInfo's tmpFolder & "/" & jsFile
			if (do shell script "test -f " & quoted form of jsSrc & " && echo YES || echo NO") = "YES" then
				do shell script "cp " & quoted form of jsSrc & " " & quoted form of scriptsDest
			end if
		end repeat
	end if
end enableMod

-- Disable mod: delete behavior and resource packs for this mod name
on disableMod(modInfo, mcPath)
	set behaviorDest to mcPath & "/behavior_packs/" & modInfo's name
	set resourceDest to mcPath & "/resource_packs/" & modInfo's name
	
	deleteFolder(behaviorDest)
	deleteFolder(resourceDest)
end disableMod

-- Main routine
on run
	-- Ask or get Minecraft EDU path
	set mcPath to getMinecraftEduPath()
	
	-- List all .bdr files in modsFolderPath
	try
		set bdrFiles to paragraphs of (do shell script "find " & quoted form of modsFolderPath & " -maxdepth 1 -name '*.bdr'")
	on error
		display dialog "No .bdr files found in " & modsFolderPath buttons {"OK"}
		return
	end try
	
	if bdrFiles = {} then
		display dialog "No .bdr files found in " & modsFolderPath buttons {"OK"}
		return
	end if
	
	-- Process each .bdr mod to get info
	set modInfos to {}
	repeat with bdrFile in bdrFiles
		try
			set modInfo to processMod(bdrFile)
			copy modInfo to end of modInfos
		on error errMsg
			display dialog "Error processing mod: " & bdrFile & return & errMsg buttons {"OK"}
		end try
	end repeat
	
	if modInfos = {} then
		display dialog "No valid mods found." buttons {"OK"}
		return
	end if
	
	-- Show mod list for user to pick one to Enable/Disable
	set modNames to {}
	repeat with m in modInfos
		set previewText to ""
		if m's preview is true then set previewText to " Preview"
		set entryText to m's name & " v" & m's version & previewText
		copy entryText to end of modNames
	end repeat
	
	set chosenModName to choose from list modNames with prompt "Select a mod to enable or disable:" without multiple selections allowed
	if chosenModName is false then return
	set chosenModName to item 1 of chosenModName
	
	-- Find the chosen mod info record
	set chosenMod to missing value
	repeat with m in modInfos
		if (m's name & " v" & m's version) is in chosenModName then
			set chosenMod to m
			exit repeat
		end if
	end repeat
	
	if chosenMod is missing value then
		display dialog "Mod not found." buttons {"OK"}
		return
	end if
	
	-- Build the info dialog text
	set previewStr to ""
	if chosenMod's preview is true then set previewStr to "Preview"
	
	set infoText to "Name: " & chosenMod's name & " v" & chosenMod's version & return & chosenMod's description & return & "Requires Education: " & chosenMod's requires_minecraft & " " & previewStr
	
	-- Show dialog with Enable/Disable
	set btnClicked to button returned of (display dialog infoText buttons {"Enable", "Disable", "Cancel"} default button "Enable")
	
	if btnClicked = "Enable" then
		enableMod(chosenMod, mcPath)
		display dialog "Mod enabled." buttons {"OK"}
	else if btnClicked = "Disable" then
		disableMod(chosenMod, mcPath)
		display dialog "Mod disabled." buttons {"OK"}
	else
		-- Cancel pressed
		return
	end if
	
	-- Clean temp unzip folders
	repeat with m in modInfos
		try
			do shell script "rm -rf " & quoted form of (m's tmpFolder)
		end try
	end repeat
end run
