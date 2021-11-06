#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Documentation Build Configuration

Django Improved User documentation build configuration file, created by
sphinx-quickstart on Thu Aug 17 10:44:16 2017.

This file is execfile()d with the current directory set to its
containing dir.

Note that not all possible configuration values are present in this
autogenerated file.

All configuration values have a default; values that are commented out
serve to show the default.

If extensions (or modules to document with autodoc) are in another directory,
add these directories to sys.path here. If the directory is relative to the
documentation root, use os.path.abspath to make it absolute, like shown here.
"""

import inspect
import sys
from operator import attrgetter
from os.path import abspath, join

import sphinx_rtd_theme  # noqa: F401
from django import setup as django_setup
from django.conf import settings as django_settings
from django.utils.encoding import force_text
from django.utils.html import strip_tags

sys.path.insert(0, abspath(join("..", "src")))
django_settings.configure(
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "improved_user.apps.ImprovedUserConfig",
    ],
    AUTH_USER_MODEL="improved_user.User",
)
django_setup()


def annotate_field(lines, field, models):
    """Add documentation based on Django field data"""
    if not hasattr(field, "verbose_name") and not hasattr(field, "help_text"):
        return lines

    if field.help_text:
        # Decode and strip any html out of the field's help text
        help_text = strip_tags(force_text(field.help_text))
    else:
        help_text = force_text(field.verbose_name).capitalize()
    # Add the model field to the end of the docstring as a param
    # using the verbose name as the description
    lines.append(":param %s: %s" % (field.attname, help_text))
    # Add the field's type to the docstring
    if isinstance(field, models.ForeignKey):
        to = field.rel.to
        lines.append(
            ":type %s: %s to :class:`~%s.%s`"
            % (field.attname, type(field).__name__, to.__module__, to.__name__)
        )
    else:
        lines.append(":type %s: %s" % (field.attname, type(field).__name__))
    return lines


def process_docstring(app, what, name, obj, options, lines):
    """Use Model or Form data to improve docstrings"""
    # https://djangosnippets.org/snippets/2533/
    # https://gist.github.com/abulka/48b54ea4cbc7eb014308
    from django.db import models
    from django.forms import BaseForm

    if inspect.isclass(obj) and issubclass(obj, models.Model):
        sorted_fields = sorted(obj._meta.get_fields(), key=attrgetter("name"))
        primary_fields = [
            field
            for field in sorted_fields
            if hasattr(field, "primary_key") and field.primary_key is True
        ]
        regular_fields = [
            field
            for field in sorted_fields
            if hasattr(field, "primary_key") and field.primary_key is False
        ]

        for field in primary_fields:
            lines = annotate_field(lines, field, models)

        for field in regular_fields:
            lines = annotate_field(lines, field, models)
    elif inspect.isclass(obj) and issubclass(obj, BaseForm):
        form = obj
        for field_name in form.base_fields:
            field = form.base_fields[field_name]
            if field.help_text:
                # Decode and strip any html out of the field's help text
                help_text = strip_tags(force_text(field.help_text))
            else:
                help_text = force_text(field.label).capitalize()
            lines.append(":param %s: %s" % (field_name, help_text))
            if field.widget.is_hidden:
                lines.append(
                    ":type %s: (Hidden) %s"
                    % (field_name, type(field).__name__)
                )
            else:
                lines.append(
                    ":type %s: %s" % (field_name, type(field).__name__)
                )

    # Return the extended docstring
    return lines


def setup(app):
    """Register the docstring processor with sphinx"""
    app.connect("autodoc-process-docstring", process_docstring)
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "django": (
        "http://docs.djangoproject.com/en/stable/",
        "http://docs.djangoproject.com/en/stable/_objects/",
    ),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "Django Improved User"
copyright = "2018 JamBon Software"
author = "Russell Keith-Magee, Andrew Pinkham"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "1.0"
# The full version, including alpha/beta/rc tags.
release = "1.0.1"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This list of exclusions will affect the files found in the paths
# specified in html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of built-in themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the built-in static files,
# so a file named "default.css" will overwrite the built-in "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
        "donate.html",
    ],
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "DjangoImprovedUserdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "DjangoImprovedUser.tex",
        "Django Improved User Documentation",
        "Russell Keith-Magee, Andrew Pinkham",
        "manual",
    ),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        "djangoimproveduser",
        "Django Improved User Documentation",
        [author],
        1,
    ),
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "DjangoImprovedUser",
        "Django Improved User Documentation",
        author,
        "DjangoImprovedUser",
        "A custom Django user that authenticates via email."  # no comma!
        "Follows authentication best practices.",
        "Miscellaneous",
    ),
]
