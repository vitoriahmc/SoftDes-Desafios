# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: raulikeda
"""
import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth
from flask_babel import Babel, _
from config import Config

APP = Flask(__name__, static_url_path='')
BABEL = Babel(APP)

DBNAME = './quiz.db'


def lambda_handler(event):
    """Executa a função do arquivo recebido do usuário e verifica sua validade."""
    try:
        import numbers

        def not_equals(first, second):
            """Verifica se os resultados das funções são iguais."""
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        exec(code, locals())

        test = []
        for index, arg in enumerate(args):
            if not 'desafio{0}'.format(ndes) in locals():
                return _("Nome da função inválido. Usar 'def desafio{0}(...)'".format(ndes))

            if not_equals(eval('desafio{0}(*arg)'.format(ndes)), resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except:
        return "Função inválida."


def converte_data(orig):
    """Converte data do formato YY/MM/DD para DD/MM/YY"""
    conv1 = orig[8:10] + '/' + orig[5:7] + '/' + orig[0:4]
    conv2 = conv1 + ' ' + orig[11:13] + ':' + orig[14:16] + ':' + orig[17:]
    return conv2


def get_quizes(user):
    """Seleciona um quiz do banco de dados."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user == 'admin' or user == 'fabioja':
        cursor.execute("SELECT id, numb from QUIZ".
                       format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        cursor.execute("SELECT id, numb from QUIZ where release < '{0}'".
                       format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def get_user_quiz(userid, quizid):
    """Seleciona um quiz a partir do usuário que o enviou."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    query = "SELECT sent,answer,result from USERQUIZ where userid = '{0}' and quizid = {1} order by sent desc"
    cursor.execute(query.format(userid, quizid))
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def set_user_quiz(userid, quizid, sent, answer, result):
    """Adiciona o quiz ao banco de dados juntamente as informações do usuário
    que o enviou e de seu resultado."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) values (?,?,?,?,?);",
                   (userid, quizid, sent, answer, result))
    #
    conn.commit()
    conn.close()


def get_quiz(id_var, user):
    """Seleciona um quiz com todas as informações referentes a ele."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user == 'admin' or user == 'fabioja':
        query = "SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {0}"
        cursor.execute(query.format(id_var))
    else:
        query = "SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {0} and release < '{1}'"
        cursor.execute(query.format(id_var, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info


def set_info(pwd, user):
    """Atualiza no banco de dados as informações de senha de um usuário."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()


def get_info(user):
    """Retorna as informações de senha e tipo de um usuário."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT pass, type from USER where user = '{0}'".format(user))
    print "SELECT pass, type from USER where user = '{0}'".format(user)
    info = [reg[0] for reg in cursor.fetchall()]
    conn.close()
    len_info = len(info)
    if len_info == 0:
        return None

    return info[0]

AUTH = HTTPBasicAuth()


APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'


@APP.route('/', methods=['GET', 'POST'])
@AUTH.login_required
def main():
    """Compara os desafios recebidos aos respectivos gabaritos e atribui um feedback.
    Também verifica a existência de novos desafios e a validade dos arquivos enviados."""
    msg = ''
    p_var = 1
    challenges = get_quizes(AUTH.username())
    sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST' and 'ID' in request.args:
        quiz = get_quiz(id, AUTH.username())
        len_quiz = len(quiz)
        if len_quiz == 0:
            msg = _("Boa tentativa, mas não vai dar certo!")
            p_var = 2
            return render_template('index.html', username=AUTH.username(),
                                   challenges=challenges, p=p_var, msg=msg)

        quiz = quiz[0]
        if sent > quiz[2]:
            msg = _("Sorry... Prazo expirado!")

        f_var = request.files['code']
        filename = './upload/{0}-{1}.py'.format(AUTH.username(), sent)
        f_var.save(filename)
        with open(filename, 'r') as fp_var:
            answer = fp_var.read()

        # lamb = boto3.client('lambda')
        args = {"ndes": id,
                "code": answer,
                "args": eval(
                    quiz[4]),
                "resp": eval(quiz[5]),
                "diag": eval(quiz[6])}

        feedback = lambda_handler(args)

        result = 'Erro'
        len_feedback = len(feedback)

        if len_feedback == 0:
            feedback = _('Sem erros.')
            result = 'OK!'

        set_user_quiz(AUTH.username(), id, sent, feedback, result)

    if request.method == 'GET':
        if 'ID' in request.args:
            id_var = request.args.get('ID')
        else:
            id_var = 1

    len_challenges = len(challenges)
    if len_challenges == 0:
        msg = _("Ainda não há desafios! Volte mais tarde.")
        p_var = 2
        return render_template('index.html', username=AUTH.username(),
                               challenges=challenges, p=p_var, msg=msg)
    else:
        quiz = get_quiz(id_var, AUTH.username())
        len_quiz = len(quiz)
        if len_quiz == 0:
            msg = _("Oops... Desafio invalido!")
            p_var = 2
            return render_template('index.html', username=AUTH.username(),
                                   challenges=challenges, p_var=p_var, msg=msg)

        answers = get_user_quiz(AUTH.username(), id_var)

    return render_template('index.html', username=AUTH.username(),
                           challenges=challenges, quiz=quiz[0], e=(sent > quiz[0][2]),
                           answers=answers, p=p_var, msg=msg, expi=converte_data(quiz[0][2]))


@APP.route('/pass', methods=['GET', 'POST'])
@AUTH.login_required
def change():
    """ Realiza a troca de senha no banco de dados, quando ela é efetuada na API."""
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        p_var = 1
        msg = ''
        if nova != repet:
            msg = _('As novas senhas nao batem')
            p_var = 3
        elif get_info(AUTH.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = _('A senha antiga nao confere')
            p_var = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), AUTH.username())
            msg = _('Senha alterada com sucesso')
            p_var = 3
    else:
        msg = ''
        p_var = 3

    return render_template('index.html', username=AUTH.username(),
                           challenges=get_quizes(AUTH.username()), p=p_var, msg=msg)


@APP.route('/logout')
def logout():
    """Realiza o logout."""
    return render_template('index.html', p=2, msg=_("Logout com sucesso")), 401


@AUTH.get_password
def get_password(username):
    """Retorna a senha de um usuário."""
    return get_info(username)


@AUTH.hash_password
def hash_pw(password):
    """Retorna o hash de uma senha."""
    return hashlib.md5(password.encode()).hexdigest()

if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=8080)


@BABEL.localeselector
def get_locale():
    """Verifica as linguages em que há tradução disponível."""
    return request.accept_languages.best_match(Config['LANGUAGES'])
