import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()


    def get_questions(self):
        with self.connection:
            result = self.cursor.execute('select id, questions from support', ()).fetchall()
            data = {}
            for row in result:
                questions = tuple(row[1].split(":"))
                data[row[0]] = questions
            return data
        
    def get_answer(self, answer_id):
        with self.connection:
            return self.cursor.execute('select answer from support where id = ?', (answer_id,)).fetchone()[0]
