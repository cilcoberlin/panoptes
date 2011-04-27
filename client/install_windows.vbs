
Const INSTALL_PATH = "C:\Program Files\Panoptes\"
Const TRACKER_NAME = "panoptes.py"

' Get the Panoptes URL from the user
Dim panoptesURL 
panoptesURL = InputBox("Please enter the full URL to your Panoptes installation", "Panoptes Installer")

' Create Panoptes' file structure
Dim oFile 
Set oFile = CreateObject("Scripting.FileSystemObject")
If oFile.FolderExists(INSTALL_PATH) <> True Then
    oFile.CreateFolder INSTALL_PATH
End If
oFile.CopyFile "tracker\" & TRACKER_NAME, INSTALL_PATH, True
Set oFile = Nothing

' Install the tracker service with the user-provided URL
Dim oShell, controlSvc
Set oShell = CreateObject("WScript.Shell")
controlSvc = "python """ & INSTALL_PATH & TRACKER_NAME & """ "
oShell.Run controlSvc & "--wait 60 stop", 0, True
oShell.Run controlSvc & "remove", 0, True
oShell.Run controlSvc & "--startup auto install --url " & panoptesURL, 0, True
oShell.Run controlSvc & "--wait 60 start", 0, True
Set oShell = Nothing

MsgBox("The Panoptes tracker was successfully installed")
