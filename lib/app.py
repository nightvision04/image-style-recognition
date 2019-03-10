
from flask import Flask,flash,request, render_template, jsonify, url_for,g, session,redirect
from werkzeug.utils import secure_filename
import cv2
import os
import parser__
import time
import datetime
import pandas as pd
import view_creator as vc
import connections as con


app = Flask(__name__,static_url_path='/static')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'static/images/downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER






def allowed_file(filename):

    ext = filename.split('.')[1]

    if ext in ALLOWED_EXTENSIONS:
        return True
    else:
        return False

def set_scope():
    '''Set session variables
    '''

    try:
        if not session['cred']:
            return False
    except:
        return False


    try:
        if not session['images']:
            print('No images yet')
    except:
        print('nothing yet!')
        session['images'] = []


    try:
        if not session['active_curators']:
            print('Setting curator to default')
    except:
        print('nothing yet!')
        session['active_curators'] = ['Overall Style']



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


# Clear images page
@app.route('/clear_images', methods= ['GET'])
def _clear_images_():
    if set_scope() == False:
        return render_template('login.html')
    [session.pop(key) for key in list(session.keys()) if (key != '_flashes' and key != 'cred')]
    return render_template('home.html')

@app.route('/logout', methods= ['GET'])
def _logout_attempt_():

    session.pop('cred')

    return redirect("/", code=302)


@app.route('/login', methods= ['POST'])
def _login_attempt_():


    if request.method == "POST":
        name = request.form['email']
        password = request.form['password']
        print(name)

        connection = con.get_connection('image_profile')
        if con.check_credentials(name,password,request.remote_addr,connection) == True:
            session['cred'] = '{0} last authenticated at {1}'.format(name,time.time())
            connection.close()
            return render_template('home.html')
        connection.close()

    return render_template('home.html')

# Default page
@app.route('/', methods= ['GET','POST'])
def _home_():

    if set_scope() == False:
        return render_template('login.html')
    files = None
    if request.method == "POST":

        print(request.files)

        # check if the post request has the file part
        if 'files[]' not in request.files:
            print('No file part')

            return 'no file sent'


        for file in request.files.getlist('files[]'):
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                print('No selected file')
                return 'nothing found'
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                filepath = app.config['UPLOAD_FOLDER']+'/'+filename
                filepath_thumb = 'static/images/downloads/thumbs/' + filepath.split('static/images/downloads/')[1]
                print('Opening file:',filepath)
                scores = model.predict_quality(filepath)
                session['images'].append([scores,filepath,filepath_thumb])


        session['images'],html = vc.gallery_view_html(session['images'],
                                    session['active_curators'])

        return html

    if request.method == "GET":

        if not session['images']:

            # Update home page related values
            return render_template('home.html')

        else:
            session['images'],html = vc.gallery_view_html(session['images'],
                                                        session['active_curators'])
            return render_template('home.html',session_view=html)


if __name__ == '__main__':
    #Loads model into session
    t1 = time.time()
    model = parser__.ImageParser()
    t2 = time.time()
    print('took {} to load models'.format(t2-t1))
    import webbrowser
    webbrowser.open('http://127.0.0.1:8090')
    app.secret_key = ".." # It is necessary to set a secret key for session vars to work.
    app.run(host="0.0.0.0", port=8090,threaded=True,debug=True)
