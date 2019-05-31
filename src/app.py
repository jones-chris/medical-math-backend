from flask_api import FlaskAPI, status
from flask import request, url_for
from src.dao.FormulaDao import FormulaDao
from src.dao.CategoryDao import CategoryDao
import config
from json import dumps

app = FlaskAPI(__name__)
formula_dao = FormulaDao(config.db_path)
category_dao = CategoryDao(config.db_path)


@app.route('/formulas', methods=['GET'])
def get_all_formulas():
    category = request.args.get('category')
    query_results = None

    # If categories query param does not exist, get all formulas.
    if category is None:
        query_results = formula_dao.get_all_formulas()
    else:
        query_results = formula_dao.get_formulas_by_category(category)

    json = dumps(query_results)
    return json, status.HTTP_200_OK


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


if __name__ == '__main__':
    app.run()
