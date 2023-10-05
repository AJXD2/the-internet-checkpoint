import sqlite3


class SQL:
    def __init__(self, db="dev.db") -> None:
        self.db = db

    def __enter__(self):
        self.con = sqlite3.connect(self.db, check_same_thread=False)
        self.cur = self.con.cursor()

        return self.con, self.cur

    def __exit__(self):
        self.con.commit()
        self.con.close()
        return True


with SQL() as (con, cur):
    pass
