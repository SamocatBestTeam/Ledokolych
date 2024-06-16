from flask import Flask, request, render_template, redirect, url_for, flash
import matplotlib
import matplotlib.pyplot
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import os

SCRIPT_DIR = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = {'docx', 'xlsx'}
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(SCRIPT_DIR, 'uploads')

# Mock data and functions
ships = [
    {'id': 1, 'name': 'САРМАТ', 'type': 'arc4', 'speed': 15},
    {'id': 2, 'name': 'EDUARD TOLL', 'type': 'arc7', 'speed': 15},
    {'id': 3, 'name': 'АРКТИКА-2', 'type': 'arc5', 'speed': 19},
]


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(request, upload_dir):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'error')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file.save(os.path.join(upload_dir, file.filename))
        flash('Файл успешно загружен', 'success')
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_configuration', methods=['GET', 'POST'])
def upload_configuration():
    if request.method == 'POST':
        upload_file(request, app.config['UPLOAD_FOLDER'])
    return render_template('upload_configuration.html')


@app.route('/ships')
def list_ships():
    return render_template('ships.html', ships=ships)


@app.route('/upload_orders', methods=['GET', 'POST'])
def upload_orders():
    if request.method == 'POST':
        upload_file(request, app.config['UPLOAD_FOLDER'])
    return render_template('upload_orders.html')


@app.route('/plan_schedule', methods=['GET', 'POST'])
def plan_schedule():
    if request.method == 'POST':
        # Pseudo code for planning schedule
        generate_gantt_chart()
        return redirect(url_for('plan_schedule'))
    return render_template('plan_schedule.html')


@app.route("/graph", methods=['GET'])
def create_graph():
    fig = go.Figure(go.Scattermapbox(
        mode="markers+lines",
        lon=[73.7, 72.7, 57.8, 44.6, 33.75],
        lat=[71.3, 73.1, 70.3, 69.9, 64.95],
        marker={'size': 10}))


    fig.add_trace(go.Scattermapbox(
        mode="markers+lines",
        lon=[72.15, 72.7, 57.8, 44.6, 40.05],
        lat=[71.3, 73.1, 70.3, 69.9, 64.95],
        marker={'size': 10}, opacity=0.9))

    fig.add_trace(go.Scattermapbox(
        mode="markers+lines",
        lon=[72.15, 72.7, 57.8, 44.6, 33.75],
        lat=[71.3, 73.1, 70.3, 69.9, 69.5],
        marker={'size': 10}, opacity=0.9))

    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ]
    )

    return fig.to_html(full_html=False)


@app.route("/diagram", methods=['GET'])
def create_diagram():
    df = pd.DataFrame([
        dict(Route="Новый порт - Рейд Мурманска", Start='2022-03-01', Finish='2022-03-15', Ship="ДЮК II"),
        dict(Route="Окно в Европу - Терминал Утренний", Start='2022-03-07', Finish='2022-03-14',
             Ship="CHRISTOPHE DE MARGERIE"),
        dict(Route="Окно в Европу - Терминал Утренний", Start='2022-03-07', Finish='2022-03-14', Ship="BORIS VILKITSKY")
    ])

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Ship", color="Route")
    fig.update_yaxes(autorange="reversed")

    return fig.to_html(full_html=False)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')