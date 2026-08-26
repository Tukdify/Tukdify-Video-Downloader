; Inno Setup script for the Tukdify Video Downloader Windows installer.
; Compiled in CI with ISCC (preinstalled on windows-latest) AFTER the
; PyInstaller build.
;
; Install model: per-user by default (no admin prompt, lands in
; {localappdata}\Programs\Tukdify Video Downloader), with an override dialog so an admin
; can still install machine-wide to Program Files.

#define MyAppName "Tukdify Video Downloader"
#define MyAppVersion "2.0.1"
#define MyAppExeName "Tukdify-Video-Downloader.exe"
#define MyAppPublisher "Tukdify"
#define MyAppContact "sourabhjangid4002@gmail.com"

[Setup]
; Stable AppId across versions to recognize upgrades
AppId={{9E2E9A68-3E2A-4F3D-8824-A6A4C25191C3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppContact={#MyAppContact}
AppSupportURL=https://github.com/Tukdify
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=Tukdify-Video-Downloader-Setup-{#MyAppVersion}
SetupIconFile=..\assets\tukdify.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ExtraDiskSpaceRequired=104857600

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any temporary runtime artifacts without touching %APPDATA% user settings or downloads
Type: filesandordirs; Name: "{app}"
