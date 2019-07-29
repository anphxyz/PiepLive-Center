; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "PiepLive Center Setting"
#define MyAppVersion "1.0"
#define MyAppPublisher "QueenB JSC"
#define MyAppURL "https://queenb.vn/"
#define MyAppExeName "pieplivemanager.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{E717CCCE-0C16-462C-808D-D940310B0ED4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\PiepLiveCenter/PiepLiveManager
DisableDirPage=yes
DisableProgramGroupPage=yes
LicenseFile=D:\anph\python\PiepLive-Center\viewer\LICENSE.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=D:\anph\python\PiepLive-Center\build app
OutputBaseFilename=pieplivemanager
SetupIconFile=D:\anph\python\PiepLive-Center\resource\icons\logo-viewer.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\anph\python\PiepLive-Center\viewer\dist\pieplivemanager\pieplivemanager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\anph\python\PiepLive-Center\viewer\dist\pieplivemanager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

