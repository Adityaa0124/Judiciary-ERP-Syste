"""
Application Factory — Initializes Flask and registers all Blueprints.
"""
from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Register Blueprints (one per service) 
    from app.auth.routes   import auth_bp
    from app.admin.routes  import admin_bp
    from app.clerk.routes  import clerk_bp
    from app.judge.routes  import judge_bp
    from app.lawyer.routes import lawyer_bp
    from app.party.routes  import party_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,   url_prefix='/admin')
    app.register_blueprint(clerk_bp,   url_prefix='/clerk')
    app.register_blueprint(judge_bp,   url_prefix='/judge')
    app.register_blueprint(lawyer_bp,  url_prefix='/lawyer')
    app.register_blueprint(party_bp,   url_prefix='/party')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app
