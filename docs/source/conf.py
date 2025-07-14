# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the package to the Python path so autodoc can find it
sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Policy Inspector"
copyright = "2025, Kamil Urbanek"
author = "Kamil Urbanek"
release = "0.2.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_click",
]

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
]

# Source file extensions
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Main document
master_doc = "index"

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]

# HTML theme options for sphinxawesome_theme
html_theme_options = {
    "show_prev_next": True,
    "show_breadcrumbs": True,
    "breadcrumbs_separator": " / ",
    "main_nav_links": {
        "Home": "/",
        "API": "/api/",
        "Examples": "/examples/",
        "GitHub": "https://github.com/cdot65/policy-inspector",
    },
}

# HTML title and description
html_title = f"{project} v{release}"
html_short_title = project
html_baseurl = "https://policy-inspector.readthedocs.io/"
html_favicon = None  # Add favicon path if available

# HTML context for custom variables in templates
html_context = {
    "display_github": True,
    "github_user": "Kanguros",  # Update with actual GitHub username
    "github_repo": "policy-inspector",  # Update with actual repo name
    "github_version": "main",
    "conf_py_path": "/docs/source/",
    "source_suffix": source_suffix,
}

# Meta tags for SEO and social media
html_meta = {
    "description": "A comprehensive tool for analyzing and inspecting firewall policies",
    "keywords": "firewall, policy, security, network, analysis, inspection",
    "author": author,
    "robots": "index, follow",
    "language": "en",
    # Open Graph tags for social media
    "og:title": project,
    "og:description": "A comprehensive tool for analyzing and inspecting firewall policies",
    "og:type": "website",
    "og:url": "https://policy-inspector.readthedocs.io/",
    "og:site_name": project,
    "og:locale": "en_US",
    # Twitter Card tags
    "twitter:card": "summary",
    "twitter:title": project,
    "twitter:description": "A comprehensive tool for analyzing and inspecting firewall policies",
}

# Custom CSS and JS files
html_css_files = [
    "custom.css",
]

html_js_files = [
    "custom.js",
]

# Versioning support
version = release
html_last_updated_fmt = "%b %d, %Y"

# Search configuration
html_search_language = "en"
