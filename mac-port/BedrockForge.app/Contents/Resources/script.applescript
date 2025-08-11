property modsFolderPath : (POSIX path of (path to home folder)) & "BedrockMods/"
property mcWorldsPath : (POSIX path of (path to home folder)) & "Minecraft Education Edition/games/com.mojang/minecraftWorlds/"

-- Read file contents helper
on readFile(thePath)
	try
		set theFile to open for access POSIX file thePath
		set theContents to read theFile as «class utf8»
		close access theFile
		return theContents
	on error
		try
			close access POSIX file thePath
		end try
		return ""
	end try
end readFile

-- Delete folder helper
on deleteFolder(folderPath)
	try
		do shell script "rm -rf " & quoted form of folderPath
	end try
end deleteFolder

-- Copy folder contents helper
on copyFolderContents(src, dest)
	do shell script "mkdir -p " & quoted form of dest
	do shell script "cp -R " & quoted form of (src & "/.") & " " & quoted form of dest
end copyFolderContents

-- Process a single .bdr mod file: unzip it to a temp folder and return paths
on processMod(bdrPath)
	set tmpUnzipFolder to "/tmp/bedrockforge_temp_unzip_" & (do shell script "date +%s%N")
	deleteFolder(tmpUnzipFolder)
	do shell script "mkdir -p " & quoted form of tmpUnzipFolder
	do shell script "unzip -qq " & quoted form of bdrPath & " -d " & quoted form of tmpUnzipFolder
	
	return tmpUnzipFolder
end processMod

-- Main
on run
	-- Get all .bdr files
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
	
	-- Get all worlds folders
	try
		set worldDirs to paragraphs of (do shell script "find " & quoted form of mcWorldsPath & " -maxdepth 1 -type d")
	on error
		display dialog "Minecraft worlds folder not found: " & mcWorldsPath buttons {"OK"}
		return
	end try
	
	if worldDirs = {} then
		display dialog "No Minecraft worlds found in " & mcWorldsPath buttons {"OK"}
		return
	end if
	
	-- Get path to this AppleScript folder (to find enable_gametest.py)
	set scriptFolder to do shell script "dirname " & quoted form of (POSIX path of (path to me))
	set pythonScriptPath to scriptFolder & "/gametest.py"
	
	-- Process each mod .bdr file
	repeat with bdrFile in bdrFiles
		try
			set modTempFolder to processMod(bdrFile)
			
			-- Check for behavior and resource folders inside the temp unzip folder
			set behaviorFolder to modTempFolder & "/behavior"
			set resourceFolder to modTempFolder & "/resource"
			
			-- For each world, copy behavior and resource packs
			repeat with worldPath in worldDirs
				if worldPath is not mcWorldsPath then
					-- Copy behavior packs
					if (do shell script "test -d " & quoted form of behaviorFolder & " && echo YES || echo NO") = "YES" then
						set behaviorDest to worldPath & "/behavior_packs/"
						copyFolderContents(behaviorFolder, behaviorDest)
					end if
					
					-- Copy resource packs
					if (do shell script "test -d " & quoted form of resourceFolder & " && echo YES || echo NO") = "YES" then
						set resourceDest to worldPath & "/resource_packs/"
						copyFolderContents(resourceFolder, resourceDest)
					end if
					
					-- Enable gametest + experimental gameplay via Python helper script
					do shell script "/usr/bin/python3 " & quoted form of pythonScriptPath & " " & quoted form of worldPath
				end if
			end repeat
			
			-- Clean up temp unzip folder
			deleteFolder(modTempFolder)
			
		on error errMsg
			display dialog "Error processing mod " & bdrFile & ": " & errMsg buttons {"OK"}
		end try
	end repeat
	
	display dialog "All mods installed" buttons {"OK"}
end run
