import sys
import os

# Добавляем текущую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.main import run

if __name__ == "__main__":
    run() 