import os
import sys
sys.path.insert(0, os.path.abspath("..")) # Add parent directory to path so we can access main.py
from main import app
# Make sure not to modify anything below this line since it is related to Vercel configuration
handler = app