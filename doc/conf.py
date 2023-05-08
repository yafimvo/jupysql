from pkgmt.github import get_repo_and_branch_for_readthedocs

repository_url, repository_branch = get_repo_and_branch_for_readthedocs(
    repository_url="https://github.com/ploomber/jupysql",
    default_branch="master",
)

###############################################################################
# Auto-generated by `jupyter-book config`
# If you wish to continue using _config.yml, make edits to that file and
# re-generate this one.
###############################################################################
author = "Ploomber"
comments_config = {"hypothesis": False, "utterances": False}
copyright = "2023"
exclude_patterns = ["**.ipynb_checkpoints", ".DS_Store",
                    "Thumbs.db", "_build", "user-guide/table_explorer_demo.ipynb"]
nb_execution_allow_errors = False
nb_execution_excludepatterns = [
    "integrations/*-connect.ipynb",
    "integrations/mssql.ipynb",
    "integrations/mysql.ipynb",
    "integrations/mariadb.ipynb",
    "integrations/clickhouse.ipynb",
    "integrations/mindsdb.ipynb",
    "integrations/questdb.ipynb",
]
nb_execution_in_temp = True
nb_execution_show_tb = True
nb_execution_timeout = 90
extensions = [
    "sphinx_togglebutton",
    "sphinx_copybutton",
    "myst_nb",
    "jupyter_book",
    "sphinx_thebe",
    "sphinx_comments",
    "sphinx_external_toc",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_book_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "matplotlib.sphinxext.plot_directive",
    "sphinx_jupyterbook_latex",
]
external_toc_exclude_missing = False
external_toc_path = "_toc.yml"
html_baseurl = ""
html_favicon = ""
html_logo = "square-no-bg-small.png"
html_sourcelink_suffix = ""
html_theme = "sphinx_book_theme"
html_theme_options = {
    "launch_buttons": {
        "notebook_interface": "jupyterlab",
        "binderhub_url": "https://binder.ploomber.io",
        "jupyterhub_url": "",
        "thebe": False,
        "colab_url": "",
    },
    "path_to_docs": "doc",
    "repository_url": repository_url,
    "repository_branch": repository_branch,
    "analytics": {"google_analytics_id": "G-JBZ8NNQSLN"},
    "home_page_in_toc": True,
    "announcement": ("To launch a tutorial, click on the 🚀 button "
                     "below! Join us on "
                     "<a href='https://ploomber.io/community/'>Slack!</a>"),
    "use_repository_button": True,
    "use_edit_page_button": False,
    "use_issues_button": True,
}
nb_execution_cache_path = ""
nb_execution_mode = "cache"
latex_engine = "pdflatex"
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "linkify",
    "substitution",
    "tasklist",
]
myst_url_schemes = ["mailto", "http", "https"]
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#auto-generated-header-anchors
myst_heading_anchors = 2

nb_output_stderr = "show"
numfig = True
plot_html_show_formats = False
plot_html_show_source_link = False
plot_include_source = True
pygments_style = "sphinx"
suppress_warnings = ["misc.highlighting_failure"]
use_jupyterbook_latex = True
use_multitoc_numbering = True


# Adding Algolia search to jupyter-book :
# https://github.com/sphinx-doc/sphinx/issues/3812#issuecomment-491256702
# Please note this is an old thread and they are working with v2 which is a legacy.
# In order to make it work with v3 we made some changes.
# Please see algolia.css and algolia.js files to read more about these changes.

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory.
html_static_path = ['_static']

# Load custom stylesheets to support Algolia search.
html_css_files = [
    'algolia.css',
    'https://cdn.jsdelivr.net/npm/@docsearch/css@3'
]

# Load custom javascript to support Algolia search. Note that the sequence
# defined below (external first) is intentional!
html_js_files = [
    ('https://cdn.jsdelivr.net/npm/@docsearch/js@3.3.3/dist/umd/index.js',
     {'defer': 'defer'}),
    ('algolia.js', {'defer': 'defer'})
]
