from flask import Flask, render_template

from app import core
from app.web import api, auth


app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.static_folder = 'frontend/' + app.config['FRONTEND']
app.static_url_path = '/static'

core.init_app(app)
# # Init apps
auth.init_app(app)
# # Init Api
api.init_app(app)


# # Default Routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html', config=app.config)


if __name__ == '__main__':
    port = 8000
    if app.config['ENVIRONMENT'] == 'local':
        port = 5000
    app.run(host='0.0.0.0', port=port)