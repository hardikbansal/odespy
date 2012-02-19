#!/usr/bin/env python
# Make API documentation of Python modules using Sphinx.

import glob, sys, os, re, shutil, commands

# The dict packages holds the name of all Python modules
# and packages that are to be included in the documentation.
# Keywords are package names (use . to separate names, as in
# the import statement), while the values are the list of
# modules in the (sub)package. An empty keyword means that
# there is no package, just a set of modules.

source_file_dirs = [os.path.join(os.pardir, os.pardir, os.pardir, 'odesolvers')]
# Here we take all modules in source_file_dirs
modules = glob.glob(os.path.join(source_file_dirs[0], '*.py'))
packages = {'odesolvers': modules}

# Exclude certain types of files
exclude_files = ['__init__.py', 'PyDSTool.py', 'setup.py']
remove = []
for package in packages:
    for module in packages[package]:
        for name in exclude_files:
            if name in module:
                remove.append((package, module))
print packages
for package, module in remove:
    packages[package].remove(module)

source_file_dirs = [os.curdir]  # abs path or relative path to this dir
docdir = 'API'  # name of subdir to contain generated documentation
project_name = 'odesolver API'
author = 'Liwei Wang and Hans Petter Langtangen'
version = '0.1'


#--------------------------------------------------------------
# Customization below this line is seldom necessary

# Clean up previously generated API document files
if os.path.isdir(docdir):
    shutil.rmtree(docdir)

module_names = []
txtfiles = []
# Generate .txt file for each module in each package

def write_txtfile(module_name, prefix=''):
    module_names.append(module_name)
    txtfile = module_name + '.txt'
    txtfiles.append(txtfile)
    if prefix:
        full_name = prefix + '.' + module_name
    else:
        full_name = module_name
    heading_underline = '='*(7 + len(full_name))
    f = open(txtfile, 'w')

    f.write("""
:mod:`%(full_name)s`
%(heading_underline)s

.. automodule:: %(full_name)s
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:
""" % vars())
    f.close()
    print 'autogenerated %(txtfile)s for module %(module_name)s' % vars()

for package in packages:
    if package != '':
        # .txt file for package
        write_txtfile(package)
    for module in packages[package]:
        module_name = os.path.basename(module[:-3])
        write_txtfile(module_name, package)

# Let Sphinx generate the files it needs:
cmd = """\
sphinx-quickstart <<EOF
%(docdir)s
n
_
%(project_name)s
%(author)s
%(version)s
%(version)s
.txt
index
n
y
n
n
n
n
y
n
n
y
y
y
EOF
""" % vars()
print cmd
#failure, output1 = commands.getstatusoutput(cmd)
failure = os.system(cmd)
if failure:
    print 'Could not run sphinx-quickstart'
    sys.exit(1)

for txtfile in txtfiles:
    shutil.move(txtfile, docdir)

# Copy figs-tut dir from the tutorial
dest = os.path.join(docdir, 'figs-tut')
if os.path.isdir(dest):
    shutil.rmtree(dest)
shutil.copytree(os.path.join(os.pardir, 'tutorial', 'figs-tut'), dest)

os.chdir(docdir)

# Insert list of modules in the file index.txt (generated by sphinx-quickstart)
module_names_formatting = '\n   '.join(module_names)
f = open('index.txt', 'r')
lines = f.readlines()
f.close()
f = open('index.txt', 'w')
for line in lines:
    if 'Welcome to' in line:
        # Remove the Welcome to ... 's documentation
        words = line.split()
        line = ' '.join(words[2:-1])[:-2] + '\n'
    f.write(line)
    if ':maxdepth:' in line:
        f.write("""
   %(module_names_formatting)s
""" % vars())
f.close()

# Edit the generated conf.py file (generated by the above command)

f = open('conf.py', 'r'); text = f.read(); f.close()

# Specify where to find the source files (.py)
source = ["os.path.abspath(os.path.join(os.pardir, '%s'))" % d
          for d in source_file_dirs]
text = re.sub(r'\#sys\.path\.insert.+', 'sys.path.extend([%s])' % \
              ', '.join(source), text)

# Also add more extensions
extensions = """\
extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.mathjax',
  #'sphinx.ext.pngmath',
  #'matplotlib.sphinxext.mathmpl',
  'sphinx.ext.viewcode',
  'numpydoc',
  'sphinx.ext.autosummary',
  'sphinx.ext.doctest',
  'matplotlib.sphinxext.only_directives',
  'matplotlib.sphinxext.plot_directive',
  'matplotlib.sphinxext.ipython_directive',
  'matplotlib.sphinxext.ipython_console_highlighting',
  'sphinx.ext.inheritance_diagram']
"""
text = re.sub(r'extensions = .*\]', extensions, text)

# Add support for other themes
themes = """\
html_theme = [
  'default',
  'agogo',
  'haiku',
  'pyramid',
  'sphinxdoc',
  'basic',
  'epub',
  'nature',
  'scrolls',
  'traditional'][0]  # standard themes in sphinx"
"""
text = text.replace("html_theme = 'default'", themes)

# Add support for customizing themes
customize_theme = """\
# See http://sphinx.pocoo.org/theming.html for setting options
# This is a customization of the default theme:
#html_theme_options = {
#  'rightsidebar': 'true',
#}
"""
text = text.replace('#html_theme_options = {}', customize_theme)

# Write modified text back to conf.py
f = open('conf.py', 'w'); f.write(text); f.close()

# Make sure we have the numpydoc module as this is needed for
# the API documentation
try:
    import numpydoc
except ImportError:
    print """\
Install numpydoc: download numpy (or get the latest github version,
cd doc/sphinxext; sudo python setup.py install
"""
    sys.exit(1)

# Generate HTML documentation
print '\n\nmake html...'
failure, output2 = commands.getstatusoutput('make html')
if 'toctree contains reference' in output2:
    output2 += '\n\nMany warnings "toctree contains reference to nonexisting document" may appear above, but this is not critical.'
for line in output2.splitlines():
    if 'ImportError' in line:
        print 'ERROR in source code specification:', line
f = open('../tmp.out', 'w')
f.write(output2)
f.close()
if failure:
    print 'Could not run make html'
    sys.exit(1)


print '\nrun google-chrome API/_build/html/index.html to see the documentation'
print '\nsee tmp.out for output from make html'


