# main screen
from server import oncher_app
from flask import render_template

@oncher_app.route('/window_2')
def window_2():
    return render_template('window2.html')
