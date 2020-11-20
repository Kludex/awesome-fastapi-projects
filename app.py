import json

import dash
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

HEADERS = ("name", "age", "dependencies")


app = dash.Dash()

with open("results.json") as json_file:
    data = json.load(json_file)

print(data)

app.layout = html.Div(
    [
        dash_table.DataTable(
            id="datatable-interactivity",
            columns=[
                {"name": i.capitalize(), "id": i, "deletable": True, "selectable": True}
                for i in HEADERS
            ],
            data=data,
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
        ),
        html.Div(id="datatable-interactivity-container"),
    ]
)


@app.callback(
    Output("datatable-interactivity", "style_data_conditional"),
    [Input("datatable-interactivity", "selected_columns")],
)
def update_styles(selected_columns):
    return [
        {"if": {"column_id": i}, "background_color": "#D2F3FF"}
        for i in selected_columns
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
