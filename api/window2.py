# main screen
from server import oncher_app
from flask import render_template
import pickle
from flask import jsonify
from flask import request
from app import BASE_URL


@oncher_app.route('/window_2')
def window_2():
    return render_template('window2.html',BASE_URL=BASE_URL)


@oncher_app.route('/save_time_count', methods=['POST'])
def save_time_count():
    f = request.form
    if f:
        a = {'hour': int(f['hour']), 'minutes': int(f['minutes']), 'seconds': int(f['seconds'])}
        print(a)
        with open('start_timer.pickle', 'wb') as handle:
            pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return jsonify(status=1)
    else:
        return jsonify(status=0)
