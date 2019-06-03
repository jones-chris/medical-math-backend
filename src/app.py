from flask_api import FlaskAPI, status
from flask import request, url_for, make_response
from src.dao.FormulaDao import FormulaDao
from src.dao.CategoryDao import CategoryDao
import config
from json import dumps

app = FlaskAPI(__name__)
formula_dao = FormulaDao(config.db_path)
category_dao = CategoryDao(config.db_path)


@app.route('/formulas', methods=['GET', 'OPTIONS'])
def get_all_formulas():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    else:
        category = request.args.get('category')
        query_results = None

        # If categories query param does not exist, get all formulas.
        if category is None:
            query_results = formula_dao.get_all_formulas()
        else:
            query_results = formula_dao.get_formulas_by_category(category)

        json = dumps(query_results)
        return _corsify_actual_response(json)


@app.route('/formulas/<int:id>', methods=['GET'])
def get_formula(id):
    query_result = formula_dao.get_formula_by_id(id)
    json = dumps(query_result)
    return json, status.HTTP_200_OK


@app.route('/categories', methods=['GET'])
def get_all_categories():
    categories = category_dao.get_all_categories()
    json = dumps(categories)
    return json, status.HTTP_200_OK


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
    app.run()
