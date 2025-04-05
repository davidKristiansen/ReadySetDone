import sphinx_rtd_theme

project = "ReadySetDone"
copyright = "2025, David Kristiansen"
author = "David Kristiansen"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_dark_mode",
    "sphinx.ext.autodoc.typehints",
    "myst_parser",
]
source_suffix = [".rst", ".md"]
templates_path = ["_templates"]
exclude_patterns = []
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "style_external_links": True,
    "navigation_depth": 4,
    "collapse_navigation": False,
    "style_nav_header_background": "#1d2021",  # optional customization
}

# html_static_path = ['_static']
