[Setup]
AppName=Hotel Management System
AppVersion=1.0
DefaultDirName={pf}\Hotel Management System
DefaultGroupName=Hotel Management System
OutputBaseFilename=hotel_management_installer
Compression=lzma
SolidCompression=yes

[Files]
; Указываем правильный путь к .exe файлу, созданному PyInstaller
Source: "F:\Hotel Management System\desktop_app\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; Добавляем базу данных
Source: "F:\Hotel Management System\hotel_management.db"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
; Создаем ярлык на рабочем столе
Name: "{commondesktop}\Hotel Management System"; Filename: "{app}\main.exe"; WorkingDir: "{app}"

[Run]
; Запускаем приложение после установки
Filename: "{app}\main.exe"; Description: "Запуск Hotel Management System"; Flags: nowait postinstall skipifsilent
