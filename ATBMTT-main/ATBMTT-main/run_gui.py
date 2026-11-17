"""Launch the desktop interface; --web opens the offline HTML interface."""
import argparse
from pathlib import Path
import webbrowser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--web', action='store_true', help='Mở giao diện web offline')
    group.add_argument('--desktop', action='store_true', help='Mở giao diện cửa sổ (mặc định)')
    args = parser.parse_args()
    if not args.web:
        from ui.gui import main as desktop_main
        desktop_main()
        return
    interface = Path(__file__).resolve().with_name('giao_dien.html')
    if not interface.is_file():
        parser.exit(1, 'Missing giao_dien.html. Run: python ui/web/build.py\n')
    if not webbrowser.open(interface.as_uri(), new=2):
        print(f'Open this file in Chrome or Edge: {interface}')


if __name__ == '__main__':
    main()
