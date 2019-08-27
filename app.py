from flask_api import FlaskAPI
from flask import request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import sys


"""
App variables
"""


app = FlaskAPI(__name__, static_folder='templates/dist/', static_url_path='')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/math.db"
db = SQLAlchemy(app)

if len(sys.argv) >= 2 and sys.argv[1] == 'PROD':
    IS_PROD = True
else:
    IS_PROD = False


"""
SQLAlchemy model classes.
"""


class AllFormulas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    abbreviation = db.Column(db.String, unique=True, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, nullable=True)
    has_children = db.Column(db.Boolean, nullable=True)
    function = db.Column(db.String, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'category': self.category_name,
            'parentId': self.parent_id,
            'hasChildren': self.has_children,
            'function': self.function
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


"""
Flask API endpoint methods.
"""


@app.route('/', methods=['GET'])
def serve_home_page():
    return app.send_static_file('index.html')


@app.route('/formulas', methods=['GET', 'OPTIONS'])
def get_all_formulas():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        category = request.args.get('category')
        search = request.args.get('search')

        if category:
            query_results = AllFormulas.query.filter(AllFormulas.category_id == category)
        elif search:
            query_results = AllFormulas.query.filter(or_(AllFormulas.name.ilike('%{}%'.format(search)),
                                                         AllFormulas.abbreviation.ilike('%{}%'.format(search))))
        else:
            # Need to use double equals in filter expression below for sqlalchemy query to work correctly.
            query_results = AllFormulas.query.filter(AllFormulas.parent_id == None)

        # Now get children (first level of descendants only...no grandchildren) of each formula.
        # for formula in query_results:
        #     child_formulas_json = formula_dao.get_child_formulas(formula['id'])
        #     formula['childFormulas'] = child_formulas_json

        json = []
        for formula in query_results:
            json.append(formula.as_dict())

        if IS_PROD:
            return json
        else:
            return _corsify_actual_response(json)


@app.route('/formulas/<int:id>', methods=['GET'])
def get_child_formulas(id):
    query_result = AllFormulas.query.filter(AllFormulas.parent_id == id)
    json = _convert_model_to_json(query_result)
    if IS_PROD:
        return json
    else:
        return _corsify_actual_response(json)


@app.route('/categories', methods=['GET'])
def get_all_categories():
    categories = Category.query.all()
    json = _convert_model_to_json(categories)
    if IS_PROD:
        return json
    else:
        return _corsify_actual_response(json)


"""
Private methods
"""


def _convert_model_to_json(query_result):
    """
    This assumes that the objects contained in the query_result parameter have a as_dict() method, which AllFormulas and
    Category classes both have.
    """
    json = []
    for obj in query_result:
        json.append(obj.as_dict())
    return json


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response_body):
    response = make_response(response_body)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


"""
Start the Flask API app.
"""


if __name__ == '__main__':
    if IS_PROD:
        print('Running in PROD mode on 0.0.0.0:80')
        app.run(host='0.0.0.0', port=80)
    else:
        print('Running in DEV mode')
        app.run()
