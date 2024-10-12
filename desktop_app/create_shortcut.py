import os
import win32com.client

def create_shortcut():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # Путь к рабочему столу
    path_to_app = r"C:\path\to\your\app.exe"  # Путь к исполняемому файлу приложения
    shortcut = os.path.join(desktop, "Hotel Management System.lnk")  # Имя ярлыка

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_obj = shell.CreateShortCut(shortcut)
    shortcut_obj.TargetPath = path_to_app
    shortcut_obj.WorkingDirectory = os.path.dirname(path_to_app)
    shortcut_obj.IconLocation = path_to_app  # Можешь указать отдельный путь к иконке, если нужно
    shortcut_obj.save()

if __name__ == "__main__":
    create_shortcut()
