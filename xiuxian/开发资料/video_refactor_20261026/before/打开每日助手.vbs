Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
folder = files.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = folder
shell.Run """C:\Users\21413\AppData\Local\Programs\Python\Python39\pythonw.exe"" """ & folder & "\ui.py""", 0, False
