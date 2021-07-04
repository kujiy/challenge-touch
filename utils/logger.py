import sys
import logging

logger = logging.getLogger('challenge')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sh)
logger.setLevel(logging.INFO)

