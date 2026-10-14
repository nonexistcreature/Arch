; Arkhaven client installer. Built by launcher/build.py (passes /DStage=... /DMyVersion=...).
#ifndef Stage
  #define Stage "build\stage"
#endif
#ifndef MyVersion
  #define MyVersion "0.0.0"
#endif

[Setup]
AppId={{6E1C2B7A-4A8F-4C55-9E2B-ARKHAVEN0001}
AppName=Arkhaven
AppVersion={#MyVersion}
AppPublisher=Arkhaven
DefaultDirName={localappdata}\Arkhaven
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputBaseFilename=Arkhaven-Setup-{#MyVersion}
SetupIconFile=assets\arkhaven.ico
UninstallDisplayIcon={app}\arkhaven.ico
WizardImageFile=assets\wizard.bmp
WizardSmallImageFile=assets\wizard_small.bmp
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ShowLanguageDialog=auto

[Languages]
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
ru.PresetTitle=Графика
ru.PresetSub=Выберите пресет. Мы уже отметили подходящий вашей видеокарте. Поменять можно в любой момент ярлыком «Arkhaven — графика».
ru.Detected=Найдена видеокарта: %1
ru.ShortcutGraphics=Arkhaven — графика
ru.ShortcutFolder=Arkhaven — папка игры
ru.LaunchNow=Запустить Arkhaven
ru.KeepUserData=Удалить также скриншоты, схематики и одиночные миры?
en.PresetTitle=Graphics
en.PresetSub=Pick a preset. We've already selected the one that suits your graphics card. You can change it any time with the "Arkhaven — graphics" shortcut.
en.Detected=Detected graphics card: %1
en.ShortcutGraphics=Arkhaven — graphics
en.ShortcutFolder=Arkhaven — game folder
en.LaunchNow=Launch Arkhaven
en.KeepUserData=Also delete screenshots, schematics and singleplayer worlds?

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#Stage}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userdesktop}\Arkhaven"; Filename: "{app}\prismlauncher.exe"; Parameters: "--launch Arkhaven"; IconFilename: "{app}\arkhaven.ico"; Tasks: desktopicon
Name: "{userprograms}\Arkhaven\Arkhaven"; Filename: "{app}\prismlauncher.exe"; Parameters: "--launch Arkhaven"; IconFilename: "{app}\arkhaven.ico"
Name: "{userdesktop}\{cm:ShortcutGraphics}"; Filename: "{app}\switch-graphics.cmd"; IconFilename: "{app}\arkhaven.ico"; Tasks: desktopicon
Name: "{userprograms}\Arkhaven\{cm:ShortcutGraphics}"; Filename: "{app}\switch-graphics.cmd"; IconFilename: "{app}\arkhaven.ico"
Name: "{userprograms}\Arkhaven\{cm:ShortcutFolder}"; Filename: "{app}\instances\Arkhaven\.minecraft"

[Run]
Filename: "{app}\prismlauncher.exe"; Parameters: "--launch Arkhaven"; Description: "{cm:LaunchNow}"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\instances\Arkhaven\.minecraft\mods"
Type: filesandordirs; Name: "{app}\instances\Arkhaven\.minecraft\config"
Type: filesandordirs; Name: "{app}\libraries"
Type: filesandordirs; Name: "{app}\meta"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\assets"

[Code]
var
  PresetPage: TInputOptionWizardPage;
  GpuName: String;

const
  PresetIds = 'fast,balanced,beautiful,ultra';

function PresetId(Index: Integer): String;
begin
  case Index of
    0: Result := 'fast';
    1: Result := 'balanced';
    2: Result := 'beautiful';
  else
    Result := 'ultra';
  end;
end;

function DetectGpu(): String;
var
  Locator, Service, Items, Item: Variant;
  I: Integer;
begin
  Result := '';
  try
    Locator := CreateOleObject('WbemScripting.SWbemLocator');
    Service := Locator.ConnectServer('.', 'root\CIMV2');
    Items := Service.ExecQuery('SELECT Name FROM Win32_VideoController');
    for I := 0 to Items.Count - 1 do
    begin
      Item := Items.ItemIndex(I);
      if (Result = '') or (Pos('Intel', Result) > 0) or (Pos('Microsoft', Result) > 0) then
        Result := Item.Name;
    end;
  except
    Result := '';
  end;
end;

function SuggestPreset(Gpu: String): Integer;
var
  G: String;
begin
  G := Uppercase(Gpu);
  Result := 1;
  if (Pos('INTEL', G) > 0) or (Pos('VEGA', G) > 0) or (Pos('MX', G) > 0) or (G = '') then Result := 0
  else if (Pos('RTX 30', G) > 0) or (Pos('RTX 40', G) > 0) or (Pos('RTX 50', G) > 0) or (Pos('RX 6', G) > 0) or (Pos('RX 7', G) > 0) or (Pos('RX 9', G) > 0) then Result := 3
  else if (Pos('RTX', G) > 0) or (Pos('RX 5', G) > 0) then Result := 2;
end;

procedure InitializeWizard();
var
  S: String;
begin
  GpuName := DetectGpu();
  S := ExpandConstant('{cm:PresetSub}');
  if GpuName <> '' then S := S + #13#10 + FmtMessage(ExpandConstant('{cm:Detected}'), [GpuName]);
  PresetPage := CreateInputOptionPage(wpSelectTasks, ExpandConstant('{cm:PresetTitle}'), '', S, True, False);
  if ActiveLanguage = 'ru' then
  begin
    PresetPage.Add('Быстро — без шейдеров (слабые ПК, ноутбуки)');
    PresetPage.Add('Сбалансировано — шейдеры, средняя дальность (GTX 1660 / RX 580)');
    PresetPage.Add('Красиво — шейдеры, большая дальность (RTX 2060 и выше)');
    PresetPage.Add('Максимум — для мощных ПК (RTX 3070+, 32 ГБ ОЗУ)');
  end else begin
    PresetPage.Add('Fast — no shaders (weak PCs, laptops)');
    PresetPage.Add('Balanced — shaders, medium distance (GTX 1660 / RX 580)');
    PresetPage.Add('Beautiful — shaders, long distance (RTX 2060 and up)');
    PresetPage.Add('Ultra — for powerful PCs (RTX 3070+, 32 GB RAM)');
  end;
  PresetPage.SelectedValueIndex := SuggestPreset(GpuName);
end;

procedure ReplaceInFile(const FileName, Token, Value: String);
var
  Lines: TArrayOfString;
  I: Integer;
begin
  if not LoadStringsFromFile(FileName, Lines) then Exit;
  for I := 0 to GetArrayLength(Lines) - 1 do
    StringChangeEx(Lines[I], Token, Value, True);
  SaveStringsToUTF8File(FileName, Lines, False);
end;

procedure ApplyPreset(const Id: String);
var
  Src, Mc, Java: String;
begin
  Src := ExpandConstant('{app}\presets\') + Id;
  Mc := ExpandConstant('{app}\instances\Arkhaven\.minecraft');
  ForceDirectories(Mc + '\config');
  { options.txt holds the player's keybinds: only seed it on first install. switch-graphics.cmd patches distances later. }
  if not FileExists(Mc + '\options.txt') then
    CopyFile(Src + '\options.txt', Mc + '\options.txt', False);
  CopyFile(Src + '\config\iris.properties', Mc + '\config\iris.properties', False);
  CopyFile(Src + '\instance.cfg', ExpandConstant('{app}\instances\Arkhaven\instance.cfg'), False);
  Java := ExpandConstant('{app}\java\bin\javaw.exe');
  StringChangeEx(Java, '\', '/', True);
  ReplaceInFile(ExpandConstant('{app}\instances\Arkhaven\instance.cfg'), '@JAVA@', Java);
  ReplaceInFile(ExpandConstant('{app}\prismlauncher.cfg'), '@JAVA@', Java);
  SaveStringToFile(ExpandConstant('{app}\preset.txt'), Id, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    ApplyPreset(PresetId(PresetPage.SelectedValueIndex));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Mc: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    Mc := ExpandConstant('{app}\instances\Arkhaven\.minecraft');
    if SuppressibleMsgBox(ExpandConstant('{cm:KeepUserData}'), mbConfirmation, MB_YESNO or MB_DEFBUTTON2, IDNO) = IDYES then
      DelTree(ExpandConstant('{app}'), True, True, True);
  end;
end;
