import os

__author__ = 'João Neto'

# Template data
name = 'Ninestars by Bootstraptaste'
short_name = 'ninestars'
description = 'Ninestars Free Bootstrap 3 theme for creative'
link = 'http://bootstraptaste.com/ninestars-free-bootstrap-3-theme-for-creative/'
file_name = 'template.html'
original_file_name = 'index.html'

# Template dirs and paths (default implementation)
base_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_path, file_name)
parent_path = os.path.abspath(os.path.dirname(base_path))
dir_name = os.path.relpath(base_path, parent_path)
