"""Compatibility entry point for the original sign-in launcher."""
import sys
from assistant import main

if __name__ == '__main__':
    check_only = '--check-only' in sys.argv[1:]
    sys.argv = [sys.argv[0], 'inspect' if check_only else 'signin']
    main()
