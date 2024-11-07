from flask import Blueprint

bp = Blueprint('curator', __name__)

@bp.route('/curator')
def some_route():
    # route implementation
    pass 