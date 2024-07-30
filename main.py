import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# TODO: Change logging level with env or/and allow to fully (dis/en)able logging somewhere?\
# Standard file handler
file_handler = TimedRotatingFileHandler("flowshiki.log", when='D', interval=1, backupCount=1, encoding='utf-8')
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
file_handler.setFormatter(formatter)

logging.basicConfig(handlers=[file_handler], level=logging.DEBUG if os.environ.get("SHK_LOGGING_DEBUG") else logging.INFO)

plugin_dir = Path.absolute(Path(__file__).parent)
sys.path = [str(plugin_dir / p) for p in (".", "lib", "plugin")] + sys.path

def run():
    from src.plugin import plugin
    plugin.run()

try:
    run()
except Exception as e:
    logging.exception(e)
