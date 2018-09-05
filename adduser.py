# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: raulikeda
"""
import sqlite3
import hashlib

def add_user(user, pwd, tipo):
    """Adiciona o usuário ao banco de dados quiz.db a partir do arquivo users.csv, juntamente
    ao seu tipo e a sua senha, que também é gerada no método utilizando a hashlib.md5."""

    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.execute('Insert into USER(user,pass,type) values("{0}","{1}","{2}");'.format(user, pwd,
                                                                                        tipo))
    conn.commit()
    conn.close()

    if __name__ == '__main__':

        with open('users.csv', 'r') as file_var:
            lines = file_var.read().splitlines()

        for users in lines:
            (user, tipo) = users.split(',')
            print user
            print tipo
            add_user(user, hashlib.md5(user.encode()).hexdigest(), tipo)
