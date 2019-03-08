
from flask import Flask,flash,request, render_template, jsonify, url_for,g, session
from werkzeug.utils import secure_filename
import cv2
import os
import parser__
import time


app = Flask(__name__,static_url_path='/static')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'downloads'
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



# Default page
@app.route('/', methods= ['GET','POST'])
def _update_version_description(id=None):
    set_scope()
    files = None
    if request.method == "POST":

        # check if the post request has the file part
        if 'files[]' not in request.files:
            print('No file part')

            return 'no file sent'

        file = request.files['files[]']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return 'nothing found'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            filepath = app.config['UPLOAD_FOLDER']+'/'+filename
            print('Opening file:',filepath)
            model.predict_quality(filepath)


            return 'success'

    if request.method == "GET":

        # Update home page related values
        return render_template('home.html',value=sql_dict.home,display_scope=session['version'])





if __name__ == '__main__':
    #Loads model into session
    t1 = time.time()
    model = parser__.ImageParser()
    t2 = time.time()
    print('took {}'.format(t2-t1))
    import webbrowser
    webbrowser.open('http://127.0.0.1:8090')
    app.secret_key = ".." # It is necessary to set a secret key for session vars to work.
    app.run(host="0.0.0.0", port=8090,threaded=True,debug=True)
