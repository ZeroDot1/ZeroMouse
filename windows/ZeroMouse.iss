#define AppVersion GetEnv("ZEROMOUSE_VERSION")
#if AppVersion == ""
  #error ZEROMOUSE_VERSION must be set when compiling the Windows installer.
#endif

[Setup]
AppId={{5B874B46-18F6-4B19-8E70-5351B5E3312E}
AppName=ZeroMouse Neon Launch
AppVersion={#AppVersion}
AppPublisher=ZeroDot1
LicenseFile=..\LICENSE
AppPublisherURL=https://github.com/ZeroDot1/ZeroMouse
AppSupportURL=https://github.com/ZeroDot1/ZeroMouse/issues
DefaultDirName={localappdata}\ZeroMouse
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
MinVersion=10.0
ArchitecturesAllowed=x86compatible
OutputDir=..\dist\windows
OutputBaseFilename=ZeroMouse-Setup-{#AppVersion}
UninstallDisplayName=ZeroMouse Neon Launch Cursor Theme
UninstallDisplayIcon={app}\Cursors\arrow.cur
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
SetupLogging=yes
CloseApplications=no
RestartIfNeededByRun=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "cursors\*"; DestDir: "{app}\Cursors"; Flags: ignoreversion
Source: "Install-Cursors.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Run]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; \
  Parameters: "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""{app}\Install-Cursors.ps1"" -Mode Install -CursorDir ""{app}\Cursors"" -BackupPath ""{app}\cursor-backup.json"""; \
  StatusMsg: "Applying ZeroMouse cursor settings for this Windows user..."; \
  Flags: runhidden waituntilterminated

[UninstallRun]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; \
  Parameters: "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""{app}\Install-Cursors.ps1"" -Mode Uninstall -CursorDir ""{app}\Cursors"" -BackupPath ""{app}\cursor-backup.json"""; \
  RunOnceId: "RestoreZeroMouseCursors"; \
  Flags: runhidden waituntilterminated
