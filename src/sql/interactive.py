import ipywidgets as widgets


button = widgets.Button(
    value=False,
    description='Run query')

textbox = widgets.Text(
    value='SELECT * FROM languages',
    description='Your SQL:',
)
