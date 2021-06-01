# py37pytorch - kimui-MacBook-Pro-3:falsk_server kimkwangil$ python app.py - notebook
# py37Falsk - home_imac
# py37Flask - office_imac


import os
import datetime
import hashlib
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash
from database import list_users, verify, delete_user_from_db, add_user
from database import read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id
from database import image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db
from werkzeug.utils import secure_filename
from flask import jsonify
import json



# sentiment classifier
from sentmentAnalysis import sentiment_analysis, Sentiments_analysis

# chatbot 
from chat import chat_start


app = Flask(__name__)
app.config.from_object('config')



@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413


### - BACKUP - ####
# @app.route("/")
# def FUN_root():
#     return render_template("index.html")


@app.route('/', methods = ['POST', 'GET'])   
def FUN_root():
    if request.method == 'POST':

        data = request.get_json()
        print("#"*100)
        # 이 데이터를 입력으로 사용해야 함
        print('data: ', data)

        # 여기에 쳇봇 코드를 넣어야 함
        data = data['id']
        print('data: ', data) 

        # 여기서 생성한 answer_ 를 html에 보내야 함
        answer_ = chat_start(data)
        print('ChatBot Answer_:', answer_)

        result_emotions = Sentiments_analysis(str(data))
        # 감성분석 결과는 콘솔에 기록됨
        print('result_emotions :' , result_emotions)
        
        ######### set ->list-> string  변환  
        result_emotions_list= list(result_emotions)
        result_emotions = ",".join(result_emotions_list)

        emotion_check(result_emotions)

        data = {
            "result_emotions" : result_emotions,
            "answer" : answer_
            
        }

        return jsonify(data)

    else: ### GET 방식 
        # result_emotions = "test"
        # answer_ = "test"
        # result_fin =  render_template("index.html",result_emotions = result_emotions, answer_ = answer_)
        result_fin =  render_template("index.html")

    return result_fin


def emotion_check(input_value):
    result = input_value
    return render_template("index.html", result_emotions = result)



@app.route('/ajax', methods=['POST'])
def ajax():
    data = request.get_json()
    # print('data: ', data) # 이 데이터를 입력으로 사용해야 함
    # 여기에 쳇봇 코드를 넣어야 함
    data = data['id']
    print('data: ', data) 
    result_emotions = Sentiments_analysis(str(data))
    print(result_emotions)

    return jsonify(result = "success", result2= result_emotions)



@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")


# index.html 에서 text 데이터를 입력 받음
# @app.route('/result', methods = ['POST', 'GET'])   
# def result():
#     if request.method == 'POST':
#         result = request.form
#         # anaysis sentiment
#         # result_ = sentiment_analysis(str(result))
#         # print(type(result))
#         # result  = result_[0] # 리스트의 첫 번째 값 가져오기
#         # print(type(result)) # 이 값은 딕셔너리여야 함
#         # get_sentiment_re = result['label']

#         result_emotions = Sentiments_analysis(str(result))
#         print(result_emotions)

#         return render_template("result.html", result_emotions = result_emotions)


@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        notes_table = zip([x[0] for x in notes_list],\
                          [x[1] for x in notes_list],\
                          [x[2] for x in notes_list],\
                          ["/delete_note/" + x[0] for x in notes_list])

        images_list = list_images_for_user(session['current_user'])
        images_table = zip([x[0] for x in images_list],\
                          [x[1] for x in images_list],\
                          [x[2] for x in images_list],\
                          ["/delete_image/" + x[0] for x in images_list])

        return render_template("private_page.html", notes = notes_table, images = images_table)
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    if session.get("current_user", None) == "ADMIN":
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users = user_table)
    else:
        return abort(401)






@app.route("/write_note", methods = ["POST"])
def FUN_write_note():
    text_to_write = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text_to_write)

    return(redirect(url_for("FUN_private")))

@app.route("/delete_note/<note_id>", methods = ["GET"])
def FUN_delete_note(note_id):
    if session.get("current_user", None) == match_user_id_with_note_id(note_id): # Ensure the current user is NOT operating on other users' note.
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))


# Reference: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_image", methods = ['POST'])
def FUN_upload_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return(redirect(url_for("FUN_private")))
        file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return(redirect(url_for("FUN_private")))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_time = str(datetime.datetime.now())
            image_uid = hashlib.sha1((upload_time + filename).encode()).hexdigest()
            # Save the image into UPLOAD_FOLDER
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_uid + "-" + filename))
            # Record this uploading in database
            image_upload_record(image_uid, session['current_user'], filename, upload_time)
            return(redirect(url_for("FUN_private")))

    return(redirect(url_for("FUN_private")))

@app.route("/delete_image/<image_uid>", methods = ["GET"])
def FUN_delete_image(image_uid):
    if session.get("current_user", None) == match_user_id_with_image_uid(image_uid): # Ensure the current user is NOT operating on other users' note.
        # delete the corresponding record in database
        delete_image_from_db(image_uid)
        # delete the corresponding image file from image pool
        image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == image_uid][0]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))



@app.route("/login", methods = ["POST"])
def FUN_login():
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
    
    return(redirect(url_for("FUN_root")))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))

@app.route("/delete_user/<id>/", methods = ['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN": # ADMIN account can't be deleted.
            return abort(403)

        # [1] Delete this user's images in image pool
        images_to_remove = [x[0] for x in list_images_for_user(id)]
        for f in images_to_remove:
            image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == f][0]
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        # [2] Delele the records in database files
        delete_user_from_db(id)
        return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)

@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exsit in database. We also need to ensure the id is valid.
        if request.form.get('id').upper() in list_users():
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            add_user(request.form.get('id'), request.form.get('pw'))
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
