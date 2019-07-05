import sqlite3


class FormulaDao:
    conn_string = None

    def __init__(self, conn_string):
        self.conn_string = conn_string


    #==========================================
    # Get all top-level formulas
    #==========================================
    def get_all_formulas(self):
        # sql = """
        # select f.id,
        #        f.name,
        #        f.abbreviation,
        #        c.name
        # from formula f
        # left join formula_relationships fr
        #   on f.id = fr.child_id
        # left join category c
        #   on f.category_id = c.id
        # """
        sql = """
        select id,
               name,
               abbreviation,
               category_name,
               parent_id,
               has_children
        from all_formulas
        where parent_id is null
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql)
            return FormulaDao.map_formula_row_to_dict(cursor)

    def get_formula_by_id(self, id):
        # sql = """
        #     select f.id,
        #            f.name,
        #            f.abbreviation,
        #            c.name
        #     from formula f
        #     left join formula_relationships fr
        #       on f.id = fr.child_id
        #     left join category c
        #       on f.category_id = c.id
        #     where f.id = ?
        # """

        sql = """
        select id,
               name,
               abbreviation,
               category_name,
               parent_id,
               has_children
        from all_formulas
        where id = ?
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (id,))
            return FormulaDao.map_formula_row_to_dict(cursor)

    def get_formulas_by_category(self, category_id):
        # sql = """
        # select f.id,
        #        f.name,
        #        f.abbreviation,
        #        c.name
        #     from formula f
        #     left join formula_relationships fr
        #       on f.id = fr.child_id
        #     left join category c
        #       on f.category_id = c.id
        #     where c.id = ?
        # """
        sql = """
        select id,
               name,
               abbreviation,
               category_name,
               parent_id,
               has_children
        from all_formulas
        where category_id = ?
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (category_id,))
            return FormulaDao.map_formula_row_to_dict(cursor)


    def get_child_formulas(self, parent_formula_id):
        sql = """
        select id,
               name,
               abbreviation,
               category_name,
               parent_id,
               has_children
        from all_formulas 
        where parent_id = ?
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (parent_formula_id,))
            return FormulaDao.map_formula_row_to_dict(cursor)


    def get_formula_by_name_or_abbr(self, search_text):
        sql = """
        select id,
               name,
               abbreviation,
               category_name,
               parent_id,
               has_children
        from all_formulas
        where instr(name, ?) > 0
           or instr(abbreviation, ?) > 0
        """

        with sqlite3.connect(self.conn_string) as conn:
            cursor = conn.execute(sql, (search_text, search_text,))
            return FormulaDao.map_formula_row_to_dict(cursor)


    @staticmethod
    def map_formula_row_to_dict(cursor):
        results = []
        for row in cursor:
            results.append({
                'id': row[0],
                'name': row[1],
                'abbreviation': row[2],
                'category_name': row[3],
                'parent_id': row[4],
                'has_children': row[5]
            })

        return results
