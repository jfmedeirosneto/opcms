import os

__author__ = 'João Neto'

# Template data
name = 'Grayscale by by Start Bootstrap'
short_name = 'grayscale'
description = 'Grayscale is a multipurpose, one page website theme featuring a dark layout along with smooth scrolling page animations'
link = 'http://startbootstrap.com/template-overviews/grayscale/'
file_name = 'template.html'
original_file_name = 'index.html'

# Template dirs and paths (default implementation)
base_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_path, file_name)
parent_path = os.path.abspath(os.path.dirname(base_path))
dir_name = os.path.relpath(base_path, parent_path)
