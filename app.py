from extract import Extract
import shutil
from convert import Convert
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask.helpers import url_for
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers.response import Response
import os
import json
import csv
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from models.db import db
from models.model import Keyword,KeywordFile

UPLOAD_FOLDER = os.path.dirname(
    os.path.abspath(__file__)) + '/uploads/'

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keywords.db'

# db = SQLAlchemy(app)

# ## MODELS ##


# class Keyword(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), unique=True, nullable=False)
#     file = db.relationship(
#         "KeywordFile", backref=db.backref('keyword', uselist=False), lazy='dynamic')
#     is_active = db.Column(db.Boolean, default=False, nullable=False)


# class KeywordFile(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     primaryfile = db.Column(db.LargeBinary(), nullable=False)
#     secondaryfile = db.Column(db.LargeBinary())

#     keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'))

#     def __repr__(self) -> str:
#         return self.name


## VIEWS ##


@app.route("/", methods=["POST", "GET"])
@cross_origin()
def upload():
    data = []
    if request.method == "POST":
        files = request.files.getlist("files[]")

        for file in files:
            if file.filename == '':
                continue
            tempdata = {}
            tempdata["filename"] = file.filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            Extract(filepath, tempdata)
            os.unlink('uploads/' + filename)
            data.append(tempdata)

    try:
        field_names = data[0].keys()
        with open('data/data.csv', mode='a', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            if not os.stat('data/data.csv').st_size > 0:
                writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(e)

    is_active = Keyword.query.filter_by(is_active=True).first()

    return jsonify(data)
#     return render_template('home.html', data=data, files=KeywordFile.query.all(), set=Keyword.query.all(), is_active=is_active)


@app.route('/api/convert', methods=["POST"])
@cross_origin()
def convert():
    clearFolder('input/')
    clearFolder('output/')

    try:
        file = request.files.get('file[]')
        file.save(f'input/{file.filename}')

        print(file.filename)
        Convert(file.filename)

        outputFile = os.listdir('output/')

        return send_from_directory('output/', path=outputFile[0], as_attachment=True)

    except Exception as e:
        print(e)
        return Response(json.dumps({'message': 'error'}),
                        status=500, mimetype='application/json')


def clearFolder(path):
    folder = path
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


@app.route('/addname', methods=["POST", "GET"])
@cross_origin()
def addName():
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            with open('data/names/newNames.txt', mode='a') as file:
                file.write(name + ' ')
            return Response(json.dumps({'message': 'success'}), status=201, mimetype='application/json')
        except Exception as e:
            print(e)
    return redirect(url_for('upload'))


@app.route('/uploadKeywords', methods=['GET', 'POST'])
@cross_origin()
def uploadKeywords():

    if request.method == 'POST':

        filename = request.form.get('filename')
        pFile = request.files.get('pFile')
        sFile = request.files.get('sFile')

        if not sFile:
            sFile = open('uploads/keywords.txt', mode='rb')
            secondaryExe = 'txt'
        else:
            secondaryExe = sFile.filename[-3:]

        if pFile.filename[-3:] != 'txt' or secondaryExe != 'txt':
            return Response(json.dumps({'message': 'Only .txt files allowed'}), status=406, mimetype='application/json')
        try:
            keyword = KeywordFile(
                name=filename, primaryfile=pFile.read(), secondaryfile=sFile.read())
            set = Keyword.query.filter_by(is_active=True).first()
            set.file.append(keyword)
            db.session.add(keyword)
            db.session.commit()

        except Exception as e:
            print(e)
            return Response(json.dumps({'message': 'Error'}), status=500, mimetype='application/json')

    is_active = Keyword.query.filter_by(is_active=True).first()
    return render_template('addKeyword.html', files=Keyword.query.filter_by(is_active=True).first().file, is_active=is_active)
    # return Response(data, status=200, mimetype='application/json')


@app.route('/addSet', methods=["POST", "GET"])
@cross_origin()
def addSet():
    if request.method == 'POST':
        setname = request.form.get('setname')
        current = request.form.get('getname')
        if setname:
            set = Keyword(name=setname)
            db.session.add(set)
            db.session.commit()
        else:
            trues = Keyword.query.filter_by(is_active=True).all()
            for t in trues:
                t.is_active = False

            current = Keyword.query.filter_by(name=current).first()
            current.is_active = True
            db.session.commit()

    is_active = Keyword.query.filter_by(is_active=True).first()

    return render_template('addSet.html', set=Keyword.query.all(), is_active=is_active)


@app.route('/deleteKeywords/<int:id>')
def deleteKeywords(id):
    try:
        file = KeywordFile.query.get(id)
        db.session.delete(file)
        db.session.commit()
        return redirect(url_for('uploadKeywords'))
    except Exception as e:
        print(e)
        return Response(json.dumps({'message': 'error'}), status=500, mimetype='application/json')


@app.route('/downloadCSV')
def downloadCSV():
    file = open('data/data.csv', mode='r', encoding="utf-8").read()
    return Response(
        file,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=data.csv"})


@app.route('/clearCSV')
def clearCSV():
    try:
        with open('data/data.csv', mode='w', encoding="utf-8") as csvfile:
            csvfile.truncate(0)
        return redirect(url_for('upload'))
    except Exception as e:
        print(e)
        return Response(json.dumps({'message': 'error'}), status=500, mimetype='application/json')


@app.route('/addstopword', methods=['POST', 'GET'])
@cross_origin()
def addStopwords():
    data = open('data/stopwords/newStopwords.txt', mode='r').read()

    if request.method == 'POST':
        file = request.files.get('file')

        if file.filename[-3:] != 'txt':
            return Response(json.dumps({'message': 'Only .txt files allowed'}), status=406, mimetype='application/json')

        file.save('data/stopwords/newStopwords.txt')
        data = open('data/stopwords/newStopwords.txt', mode='r').read()

    return render_template('uploadStopwords.html', data=data)

if __name__ == "__main__":
  app.run()
