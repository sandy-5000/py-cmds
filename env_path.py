import os
import winreg
import ctypes

class PathEditor:
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    def get_system_path(self):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            )
            system_path, _ = winreg.QueryValueEx(registry_key, "PATH")
            winreg.CloseKey(registry_key)
            return system_path
        except FileNotFoundError:
            return ''


    def set_to_system_path(self, new_path):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(registry_key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(registry_key)
        except PermissionError:
            print("Permission denied. Please run the script as an Administrator.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def get_local_path(self):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0, winreg.KEY_READ
            )
            user_path, _ = winreg.QueryValueEx(registry_key, "PATH")
            winreg.CloseKey(registry_key)
            return user_path
        except FileNotFoundError:
            return ''
        except Exception as e:
            print(f"An error occurred while reading the user PATH: {e}")
            return ''


    def set_local_path(self, new_path):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(registry_key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(registry_key)
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x1A, 0, 0)
        except Exception as e:
            print(f"An error occurred while setting the user PATH: {e}")


    def get_path(self):
        if self.is_admin():
            return self.get_system_path()
        else:
            return self.get_local_path()


    def set_path(self, new_path):
        if self.is_admin():
            self.set_to_system_path(new_path)
        else:
            self.set_local_path(new_path)


    def position_in_range(self, position, insert=False):
        paths = self.get_path()
        paths = paths.split(';')
        k = 1 if insert else 0
        return 1 <= position <= len(paths) + k


    def add_path(self, position=1):
        if not self.position_in_range(position, True):
            raise Exception('Enter position in the given path index range')
        print()
        new_path_location = input('Path: ').strip()
        paths = self.get_path().split(';')
        paths.insert(position - 1, new_path_location)
        new_path, visited_paths = [], set()
        for path in paths:
            path = path.strip()
            if path in visited_paths:
                continue
            new_path.append(path)
            visited_paths.add(path)
        new_path = ';'.join(new_path)
        self.set_path(new_path)
        self.print_paths()


    def delete_path(self, position=None):
        if position == None:
            raise Exception('Enter a valid position')
        if not self.position_in_range(position):
            raise Exception('Enter position in the given path index range')
        print(position)
        paths = self.get_path().split(';')
        paths.pop(position - 1)
        new_path, visited_paths = [], set()
        for path in paths:
            path = path.strip()
            if path in visited_paths:
                continue
            new_path.append(path)
            visited_paths.add(path)
        new_path = ';'.join(new_path)
        self.set_path(new_path)
        self.print_paths()


    def print_paths(self):
        paths = self.get_path()
        paths = paths.split(';')
        right_just_length = len(str(len(paths)))
        print('\n ---- PATHS: ---- \n')
        for i, path, in enumerate(paths, start=1):
            print(f'{str(i).rjust(right_just_length)}) {path}')
        print('\n')


def print_options():
    print('Key Options:')
    options = [
        '> (Q or q) to Quit',
        '> (P or p) to Print PATH',
        '> (I or i) to Insert --- Format: <I or i> <position (optional, default=1)>',
        '> (D or d) to Delete --- Format: <D or d> <position>',
        '> (H or h) for Help',
    ]
    for option in options:
        print(option)

def get_postion(prompt, default=None):
    if prompt == '':
        return default
    position, *_ = prompt.split()
    try:
        return int(position)
    except:
        return default


path_editor = PathEditor()


path_editor.print_paths()
print_options()

while True:
    prompt = input('>> ').strip()

    if prompt == '':
        prompt = 'H'

    option, *rem = prompt.split()
    rem = ' '.join([i for i in rem if i])

    if option.upper() == 'Q':
        break
    elif option.upper() == 'P':
        path_editor.print_paths()
    elif option.upper() == 'I':

        position = get_postion(rem, 1)
        try:
            path_editor.add_path(position)
        except Exception as e:
            print(str(e))

    elif option.upper() == 'D':

        position = get_postion(rem)
        try:
            path_editor.delete_path(position)
        except Exception as e:
            print(str(e))

    else:
        print_options()
