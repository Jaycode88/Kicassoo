#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv

if __name__ == "__main__":
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    # Existing code
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kicassoo_store.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
