import ipywidgets as widgets


button = widgets.Button(
    value=False,
    description='Test')

textbox = widgets.Text(
    value='SELECT * FROM languages',
    description='Your SQL:',
)
