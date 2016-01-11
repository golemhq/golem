from waitress import serve
import app
import logging


logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

serve(app.app, host='0.0.0.0', port=80, threads=8)