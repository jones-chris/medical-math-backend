from flask_api import FlaskAPI
from flask import request, make_response
from src.dao.FormulaDao import FormulaDao
from src.dao.CategoryDao import CategoryDao
import config
from json import dumps

app = FlaskAPI(__name__, static_folder='templates/dist/', static_url_path='')
formula_dao = FormulaDao(config.db_path)
category_dao = CategoryDao(config.db_path)


@app.route('/', methods=['GET'])
def serve_home_page():
    return app.send_static_file('index.html')


@app.route('/formulas', methods=['GET', 'OPTIONS'])
def get_all_formulas():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    else:
        category = request.args.get('category')
        search = request.args.get('search')
        query_results = None

        if category:
            query_results = formula_dao.get_formulas_by_category(category)
        elif search:
            query_results = formula_dao.get_formula_by_name_or_abbr(search)
        else:
            query_results = formula_dao.get_all_formulas()

        # Now get children (first level of descendants only...no grandchildren) of each formula.
        # for formula in query_results:
        #     child_formulas_json = formula_dao.get_child_formulas(formula['id'])
        #     formula['childFormulas'] = child_formulas_json

        json = dumps(query_results)
        # json = []
        # for formula in query_results:
        #     json.append(formula.as_dict())
        return _corsify_actual_response(json)


@app.route('/formulas/<int:id>', methods=['GET'])
def get_child_formulas(id):
    query_result = formula_dao.get_child_formulas(id)
    json = dumps(query_result)
    return _corsify_actual_response(json)


@app.route('/categories', methods=['GET'])
def get_all_categories():
    categories = category_dao.get_all_categories()
    json = dumps(categories)
    return _corsify_actual_response(json)


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response_body):
    response = make_response(response_body)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
