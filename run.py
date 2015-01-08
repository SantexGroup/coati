import logging
import os
from app import app

# create console handler and set level to debug
path = os.path.dirname(os.path.abspath(__file__))
ch = logging.FileHandler(path + '/logs/app.log')
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
app.logger.addHandler(ch)


if __name__ == '__main__':
    port = 8000
    if app.config['ENVIRONMENT'] == 'local':
        port = 5000
    app.run(host='0.0.0.0', port=port)