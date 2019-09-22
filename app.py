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


class FormulaContexts(db.Model):
    formula_id = db.Column(db.Integer, primary_key=True)
    column_name = db.Column(db.String, nullable=False)
    col_sequence = db.Column(db.Integer, primary_key=True)
    #value_name = db.Column(db.String, nullable=False)
    value_sequence = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False)
    can_compare_result = db.Column(db.Boolean, nullable=False)

    def as_dict(self):
        return {
            'formulaId': self.formula_id,
            'colSequence': self.col_sequence,
            'valueSequence': self.value_sequence,
            'columnName': self.column_name,
            #'valueName': self.value_name,
            'value': self.value,
            'canCompareResult': self.can_compare_result
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


@app.route('/formula-context/<string:id>', methods=['GET'])
def get_formula_context(id):
    result = request.args.get('result')
    if result is not None:
        result = float(result)

    query_result = FormulaContexts.query.filter(FormulaContexts.formula_id == id)

    # Get column set (unique) from query results.
    columns = []
    for row in query_result:
        row_dict = row.as_dict()
        col_sequence = row_dict['colSequence']

        col_sequence_already_exists = False
        for column in columns:
            if column['colSequence'] == col_sequence:
                col_sequence_already_exists = True
                break

        if not col_sequence_already_exists:
            columns.append({
                'colSequence': col_sequence,
                'columnName': row_dict['columnName']
            })

    # Get rows dict
    rows_dict = []
    current_row = []
    row_sequence = 0
    for obj in query_result:
        obj_dict = obj.as_dict()
        if obj_dict['valueSequence'] == row_sequence:
            current_row.append(obj_dict)
        else:
            row_sequence = obj_dict['valueSequence']
            rows_dict.append(current_row.copy())  # Make a copy, because we are going to clear the list in the next line
            current_row.clear()
            current_row.append(obj_dict)
    rows_dict.append(current_row)  # This is for the last item in the query_result object.  Please clean this up later!

    json = {
        'columns': columns,
        'values': rows_dict
    }

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

def _get_keys_from_list_of_dicts(l):
    keys = []
    for dic in l:
        key = dic


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
