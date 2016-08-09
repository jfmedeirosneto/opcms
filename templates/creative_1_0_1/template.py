import os

__author__ = 'João Neto'

# Template data
name = 'Creative by Start Bootstrap'
short_name = 'creative'
description = 'A one page Bootstrap theme with flexible options for creative portfolios and businesses'
link = 'http://startbootstrap.com/template-overviews/creative/'
file_name = 'template.html'
original_file_name = 'index.html'

# Template dirs and paths (default implementation)
base_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_path, file_name)
parent_path = os.path.abspath(os.path.dirname(base_path))
dir_name = os.path.relpath(base_path, parent_path)
