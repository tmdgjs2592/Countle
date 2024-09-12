import os

from flask import Flask
from gensim.models import KeyedVectors

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_url_path='/static')

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
# /Users/johnlee/Downloads/GoogleNews-vectors-negative300.bin
# /Users/tmdgj/Downloads/GoogleNews-vectors-negative300.bin/GoogleNews-vectors-negative300.bin
    model_path = '/Users/tmdgj/Downloads/GoogleNews-vectors-negative300.bin/GoogleNews-vectors-negative300.bin'  # Update the path to your model file
    app.config['WORD2VEC_MODEL'] = KeyedVectors.load_word2vec_format(model_path, binary=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route('/you')
    def you():
        return "you!"
    with app.app_context():
        from . import db
        db.init_app(app)

        from . import auth
        app.register_blueprint(auth.bp)
    

    
    return app