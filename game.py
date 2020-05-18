import flask
import sqlite3
from flask import request, render_template, redirect, session, flash, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/positive_integer/v1/games/positiveInteger")
def index():
    if not session['round']:
        session['round'] = 0
    conn = sqlite3.connect('positive_integer.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM players_data")
    data = cur.fetchall()
    return render_template('index.html', data=data)


@app.route("/add", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        add_player_name = request.form['add_player']
        try:
            add_player_number = int(request.form['number'])
        except ValueError:
            print(f"Only integers!")
            flash('Only integers!')
            return redirect('/positive_integer/v1/games/positiveInteger')

        conn = sqlite3.connect('positive_integer.db')
        cursor = conn.cursor()
        sqlite_insert_query = f"INSERT INTO players_data (player_name,player_number) " \
                              f"VALUES  {add_player_name, add_player_number};"
        count = cursor.execute(sqlite_insert_query)
        conn.commit()
        cursor.close()

        return redirect('/positive_integer/v1/games/positiveInteger')


@app.route("/game", methods=["GET", "POST"])
def player_one():
    if request.method == "POST":
        conn = sqlite3.connect('positive_integer.db')
        cursor = conn.cursor()
        all_players = cursor.execute('SELECT * FROM players_data;').fetchall()
        all_players_name = cursor.execute('SELECT player_name FROM players_data;').fetchall()
        players = ""
        for i in all_players_name:
            players += i[0] + ","
        try:
            minimum = min(all_players, key=lambda t: t[1])
            session['round'] += 1
            session.pop('_flashes', None)

            conn = sqlite3.connect('positive_integer.db')
            cursor = conn.cursor()

            round_num = 'Round number: ' + str(session['round'])
            name = 'Winner: ' + str(minimum[0])
            number = 'Winning number: ' + str(minimum[1])
            players = 'Players in the round: ' + players

            query_rounds = f"INSERT INTO rounds (round_number,round_result,winner,participants) " \
                           f"VALUES  {round_num, name, number, players};"
            insert_rounds = cursor.execute(query_rounds)
            query_delete = f"DELETE FROM players_data;"
            delete_players_data = cursor.execute(query_delete)
            conn.commit()
            cursor.close()

            return f"{minimum[0]} is the winner, and the number is {minimum[1]}!"

        except:
            flash("No players added!")
            print("No players added!")
            return redirect('/positive_integer/v1/games/positiveInteger')


@app.route("/results", methods=["GET", "POST"])
def get_results():
    if request.method == "POST":
        conn = sqlite3.connect('positive_integer.db')
        cursor = conn.cursor()
        rounds = cursor.execute('SELECT * FROM rounds;')
        result = jsonify(list(rounds))
        cursor.close()
    return result


app.run()
