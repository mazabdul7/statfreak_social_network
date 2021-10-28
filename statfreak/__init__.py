import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from statfreak.configmodule import DevelopmentConfig
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
photos = UploadSet('photos', IMAGES)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(DevelopmentConfig())
    else:
        app.config.from_object(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    configure_uploads(app, photos)

    from statfreak.models import User
    from statfreak.models import Profile
    from statfreak.models import Area
    with app.app_context():
        db.create_all()

    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from statfreak.community.views import community_bp
    app.register_blueprint(community_bp)

    from statfreak.main.views import main_bp
    app.register_blueprint(main_bp)

    from statfreak.auth.views import auth_bp
    app.register_blueprint(auth_bp)

    @app.errorhandler(404)
    def err404(e):
        return render_template('404.html', error="404"), 404

    @app.errorhandler(500)
    def err500(e):
        return render_template('404.html', error="500"), 500

    @app.errorhandler(410)
    def err410(e):
        return render_template('404.html', error="410"), 410

    @app.errorhandler(403)
    def err403(e):
        return render_template('404.html', error="403"), 403

    @app.errorhandler(400)
    def err400(e):
        return render_template('404.html', error="400"), 400

    with app.app_context():
        # Import Dash application
        from statfreak.dashapp.dashboard import init_dashboard as dashone
        from statfreak.dashapp.dashboard2 import init_dashboard as dashtwo
        app = dashone(app)
        app = dashtwo(app)

    #Fixes the callback issue with CSRF and Dash callbacks
    csrf._exempt_views.add('dash.dash.dispatch')

    return app
