
import win32gui

def find_window_by_title_substring(substr):
    matches = []
    def enum_handler(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title and substr.lower() in title.lower() and win32gui.IsWindowVisible(hwnd):
            matches.append((hwnd, title))
    win32gui.EnumWindows(enum_handler, None)
    return matches

def get_client_rect_screen(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    (x0, y0) = win32gui.ClientToScreen(hwnd, (left, top))
    (x1, y1) = win32gui.ClientToScreen(hwnd, (right, bottom))
    return x0, y0, x1 - x0, y1 - y0
