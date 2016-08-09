import os

__author__ = 'João Neto'

# Template data
name = 'Agency by Start Bootstrap'
short_name = 'agency'
description = 'Agency is a stylish, one page Bootstrap theme for agencies and small businesses. The design of Agency\
 is based off of the Golden PSD Theme by Mathavan Jaya. You can download the PSD verison of this theme at\
 FreebiesXpress.com'
link = 'http://startbootstrap.com/template-overviews/agency/'
file_name = 'template.html'
original_file_name = 'index.html'

# Template dirs and paths (default implementation)
base_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_path, file_name)
parent_path = os.path.abspath(os.path.dirname(base_path))
dir_name = os.path.relpath(base_path, parent_path)
