from flask import Flask,request, render_template, jsonify, url_for,g, session



def set_scope():
    '''Set session variables
    '''
    try:
        session['version'] = "Version 1.0"
        return True
    except ValueError:
        return False


class SqlDict():
    '''This dictionary will contain the responses from a future mysql database, which
    will then be passed into the flask app to be rendered.
    '''


    def update_strategies(self):
        '''Updates dict values used by strategies page
        '''
        self.get_sorted_view=con.get_sorted_view()


sql_dict = SqlDict()
sql_dict.home=""
sql_dict.get_sorted_view=""

app = Flask(__name__,static_url_path='/static')

# Default page is workers for now - will be Main dashboard
@app.route('/')
def index_():

    set_scope()
    # Update home page related values
    return render_template('home.html',value=sql_dict.home,display_scope=session['version'])


import webbrowser
webbrowser.open('http://127.0.0.1:8090')

if __name__ == '__main__':

    app.secret_key = ".." # It is necessary to set a secret key for session vars to work.
    app.run(host="0.0.0.0", port=8090,threaded=True,debug=True)
