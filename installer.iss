; Script de Inno Setup para crear el instalador de SimClic
#define MyAppName "Horarios SimClic"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Universidad"
#define MyAppExeName "SimClic.exe"

[Setup]
AppId={{C444B8CD-CAA9-44D3-A3D9-6516901630BD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=C:\Users\jeanp\OneDrive\Documentos\Simclic\dist_installer
OutputBaseFilename=SimClic_Instalador_v1.0
SetupIconFile=C:\Users\jeanp\OneDrive\Documentos\Simclic\assets\app_icon.ico
UninstallIconFile=C:\Users\jeanp\OneDrive\Documentos\Simclic\assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\jeanp\OneDrive\Documentos\Simclic\dist\SimClic\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
