import sqlite3


class FormulaDao:
    conn_string = None

    def __init__(self, conn_string):
        self.conn_string = conn_string

    def get_all_formulas(self):
        sql = """
        select f.id,
               f.name, 
               f.abbreviation, 
               c.name
        from formula f
        left join formula_relationships fr
          on f.id = fr.child_id
        left join category c
          on f.category_id = c.id
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql)
            return FormulaDao.map_formula_row_to_dict(cursor)

    def get_formula_by_id(self, id):
        sql = """
            select f.id,
                   f.name, 
                   f.abbreviation, 
                   c.name
            from formula f
            left join formula_relationships fr
              on f.id = fr.child_id
            left join category c
              on f.category_id = c.id
            where f.id = ?
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (id,))
            return FormulaDao.map_formula_row_to_dict(cursor)

    def get_formulas_by_category(self, category_id):
        sql = """
        select f.id,
               f.name, 
               f.abbreviation, 
               c.name
            from formula f
            left join formula_relationships fr
              on f.id = fr.child_id
            left join category c
              on f.category_id = c.id
            where c.id = ?
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (category_id,))
            return FormulaDao.map_formula_row_to_dict(cursor)

    @staticmethod
    def map_formula_row_to_dict(cursor):
        results = []
        for row in cursor:
            results.append({
                'id': row[0],
                'name': row[1],
                'abbreviation': row[2],
                'category_name': row[3]
            })

        return results
