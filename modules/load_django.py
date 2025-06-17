import os
import sys
import django

sys.path.append(r'C:\Users\Admin\projects\rozetkacomua_project\rozetkacomua_project')
os.environ["DJANGO_SETTINGS_MODULE"] = "rozetkacomua_project.settings"
django.setup()