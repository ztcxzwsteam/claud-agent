import sys
import os

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AGENT_DIR)

from core.memory.memory_manager import MemoryManager

print("Attributes of MemoryManager:")
for attr in dir(MemoryManager):
    if not attr.startswith("__"):
        print(f" - {attr}")
