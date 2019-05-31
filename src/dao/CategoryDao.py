import sqlite3


class CategoryDao:
    conn_string = None

    def __init__(self, conn_string):
        self.conn_string = conn_string

    def get_all_categories(self):
        sql = """
        select id, name from category
        """

        results = []

        with sqlite3.connect(self.conn_string) as conn:
            query_results = conn.execute(sql)

            for row in query_results:
                results.append({
                    'id': row[0],
                    'name': row[1]
                })

        return results
