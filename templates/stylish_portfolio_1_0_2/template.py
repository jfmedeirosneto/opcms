import os

__author__ = 'João Neto'

# Template data
name = 'Stylish by Start Bootstrap'
short_name = 'stylish'
description = 'Stylish Portfolio is a one page Bootstrap portfolio theme with off canvas navigation and smooth\
 scrolling through content sections'
link = 'http://startbootstrap.com/template-overviews/stylish-portfolio/'
file_name = 'template.html'
original_file_name = 'index.html'

# Template dirs and paths (default implementation)
base_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_path, file_name)
parent_path = os.path.abspath(os.path.dirname(base_path))
dir_name = os.path.relpath(base_path, parent_path)
