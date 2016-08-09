import os

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

# OpCMS application
import opcms
from settings import MODULES_PATH, TEMPLATES_PATH

application = opcms.get_opcms_app(MODULES_PATH, TEMPLATES_PATH)