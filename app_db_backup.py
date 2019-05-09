# This Python file uses the following encoding: utf-8
# coding=<utf-8>
from __future__ import unicode_literals
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import configargparse
from onmt.utils.logging import init_logger
from onmt.utils.misc import split_corpus
from onmt.translate.translator import build_translator
import onmt.opts as opts
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask import url_for, redirect
import json

import os


def translate_eng(input_Esan,model):
    input_file="corpus/input.txt"
    output_file="corpus/output.txt"
    f = open(input_file, "w",encoding="UTF-8")
    f.write(input_Esan)
    f.close()
    open( output_file, "w", encoding="UTF-8").close()
    parser = configargparse.ArgumentParser(
        description='translate.py',
        config_file_parser_class=configargparse.DefaultConfigFileParser,
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter, add_env_var_help=True)
    opts.config_opts(parser)
    opts.translate_opts(parser)
    s = "-model " + model +" -src "+input_file+" -output "+output_file
    opt = parser.parse_args(s)
    main(opt)
    f = open(output_file, "r",encoding="UTF-8")
    content = ""
    if f.mode == 'r':
        content = f.read()
        f.close()
    return content


def translate_esan(input_eng,model):
    input_file="corpus/input.txt"
    output_file="corpus/output.txt"
    f = open(input_file, "w",encoding="UTF-8")
    f.write(input_eng)
    f.close()
    open( output_file, "w", encoding="UTF-8").close()
    parser = configargparse.ArgumentParser(
        description='translate.py',
        config_file_parser_class=configargparse.DefaultConfigFileParser,
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter, add_env_var_help=True)
    opts.config_opts(parser)
    opts.translate_opts(parser)
    s = "-model " + model + " -src " + input_file + " -output " + output_file
    opt = parser.parse_args(s)
    main(opt)
    f = open(output_file, "r",encoding="Utf-8")
    content = ""
    if f.mode == 'r':
        content = f.read()
        f.close()
    return content


def clean_string(string):
    string = string.replace("\n", " ")
    return string

def voice(st,file_name):
    with open(file_name, encoding="utf8") as myfile:
        count = 0
        for line in myfile:
            if line.strip() == st:
                return count
            count =count+1
    return 0

def main(opt):
    translator = build_translator(opt, report_score=True)
    src_shards = split_corpus(opt.src, opt.shard_size)
    tgt_shards = split_corpus(opt.tgt, opt.shard_size) \
        if opt.tgt is not None else [None]*opt.shard_size
    shard_pairs = zip(src_shards, tgt_shards)
    for i, (src_shard, tgt_shard) in enumerate(shard_pairs):
        #logger.info("Translating shard %d." % i)
        translator.translate(
            src=src_shard,
            tgt=tgt_shard,
            src_dir=opt.src_dir,
            batch_size=opt.batch_size,
            attn_debug=opt.attn_debug
            )


app = Flask(__name__)
FlaskJSON(app)
STATUS_OK = "ok"
STATUS_ERROR = "error"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'translator'
mysql = MySQL(app)


@app.route('/')
def gui():
    return render_template('app25.html')


@app.route('/signUpGui')
def signUpGui():
    return render_template('sign_up.html')


@app.route('/signInGui')
def signInGui():
    return render_template('sign_in.html')


@app.route('/translate', methods=["POST"])
def translate():
    if request.form['dropdown'] == "":
        return json_response(status="failed", error="Select Target language.")
    elif request.form['textbox1'] == "":
        return json_response(status="failed", error="Insert Text.")
    else:
        eng_esan_model = "Model/EngToEsan/model_step_31000.pt"
        # eng_esan_model = "Model/EngToEsan/model-model_step_50000.pt"
        esan_eng_mdel = "Model/EsantoEng/model_step_28000.pt"
        t_language = request.form['dropdown']
        input_text = request.form['textbox1']
        if input_text != "":
            input_text = clean_string(input_text)
            if t_language == "Esan":
                output = clean_string(translate_esan(input_text, eng_esan_model))
                return json_response(status="success", input=input_text, output=output)
            elif t_language == "English":
                output = clean_string(translate_eng(input_text, esan_eng_mdel))
                return json_response(status="success", input=input_text, output=output)
            else:
                return json_response(status="failed", error="Wrong Target Language")
        else:
            return json_response(status="failed", error="No Input")


@app.route('/toggle', methods=["POST"])
def eng_esan():
    eng_esan_model = "Model/EngToEsan/model_step_31000.pt"
    # eng_esan_model="Model/EngToEsan/model-model_step_50000.pt"
    esan_eng_mdel="Model/EsantoEng/model_step_28000.pt"
    t_language = request.form['dropdown']
    input_text = request.form['textbox2']
    if input_text != "":
        input_text = clean_string(input_text)
        if t_language == "English":
            output = clean_string(translate_esan(input_text, eng_esan_model))
            return json_response(status="success",input=input_text, output=output,t_lang="Esan")
        elif t_language == "Esan":
            output = clean_string(translate_eng(input_text, esan_eng_mdel))
            return json_response(status="success",input=input_text, output=output,t_lang="English")
        else:
            return json_response(status="failed", error="Wrong Target Language")
    else:
        if t_language == "English":
            return json_response(status="success", input=input_text, output="", t_lang="Esan")
        elif t_language == "Esan":
            return json_response(status="success", input=input_text, output="", t_lang="English")


@app.route('/sign_up', methods=['POST'])
def sign_up():
    try:
        request.form['email_id'] and request.form['password']
        if not request.form['email_id'] :
            return json_response(status="failed", error="Enter email_id")
        elif not request.form['password']:
            return json_response(status="failed", error="Enter password")
        else:
            email_id = request.form['email_id']
            password = request.form['password']
            try:
                cur = mysql.connection.cursor()
                try:
                    a=cur.execute("INSERT INTO user_profile(email_id, password,saved, history) VALUES (%s, %s, %s, %s)", (email_id, password,"null","null"))
                    mysql.connection.commit()
                    cur.close()
                    return json_response(status="success", email_id=email_id)
                except:
                    return json_response(status="failed", error="User already exist")
            except:
                return json_response(status="failed", error="SQL Error")
    except :
        return json_response(status="failed", error="Incomplete Parameters")


@app.route('/sign_in', methods=['POST'])
def sign_in():
    try:
        request.form['email_id'] and request.form['password']
        if not request.form['email_id']:
            return json_response(status="failed", error="Enter email_id")
        elif not request.form['password']:
            return json_response(status="failed", error="Enter password")
        else:
            email_id = request.form['email_id']
            password = request.form['password']
            try:
                cur = mysql.connection.cursor()
                query=cur.execute("SELECT saved FROM user_profile where email_id=%s and password=%s",(email_id, password,))
                mysql.connection.commit()
                if(query == 1):
                    result = cur.fetchall()
                    # print(result)
                    cur.close()
                    if result:
                       content ={'saved':result[0], 'email_id':email_id}
                       return json_response(status="success", data=content)
                    else:
                        return json_response(status="failed", error="No saved data")
                else:
                    return json_response(status="failed", error="Email or Password do not Match")
            except:
                return json_response(status="failed", error="SQL Error")
    except:
        return json_response(status="failed", error="Incomplete Parameters")


@app.route('/update_saved', methods=['POST'])
def update_saved():
    try:
        request.form['email_id'] and request.form['new_data']
        if not request.form['email_id']:
            return json_response(status="failed", error="Enter Email id")
        elif not request.form['new_data']:
            return json_response(status="failed", error="Empty saved")
        else:
            email_id = request.form['email_id']
            new_data = request.form['new_data']
            cur = mysql.connection.cursor()
            query = cur.execute("SELECT saved FROM user_profile WHERE email_id = %s", (email_id,))
            mysql.connection.commit()
            if query == 1:
                result = cur.fetchall()
                if result[0][0] =="null":
                    L = new_data
                else:
                    L= result[0][0]+"/"+new_data
                try:
                    other_query = cur.execute("UPDATE user_profile SET saved=%s WHERE email_id=%s",(str( L), email_id,))
                    mysql.connection.commit()
                    if other_query==1:
                        return json_response(status="success")
                    else:
                        return json_response(status="failed", error="Saved have not updated")
                except (MySQL.Error, MySQL.Warning) as e:
                    return json_response(status="failed", error=e)
                else:
                    return json_response(status="failed", error="No data")
            cur.close()
    except:
        return json_response(status="failed", error="Incomplete Parameters")


@app.route('/get_saved', methods=['POST'])
def get_saved():
    try:
        request.form['email_id']
        if not request.form['email_id']:
            return json_response(status="failed", error="Enter email_id")
        else:
            email_id = request.form['email_id']
            try:
                cur = mysql.connection.cursor()
                query = cur.execute("Select saved from user_profile WHERE email_id = %s",(email_id,))
                mysql.connection.commit()
                if query == 1:
                    result = cur.fetchall()
                    cur.close()
                    if result:
                        return json_response(status="success", saved=result[0][0],email_id=email_id)
                    else:
                        return json_response(status="failed", error="No history")
                else:
                    return json_response(status="failed", error="Parameter values are not correct")
            except:
                return json_response(status="failed", error="SQL Error")
    except:
        return json_response(status="failed", error="Incomplete Parameters")


@app.route('/view_history', methods=['POST'])
def view_history():
    try:
        request.form['email_id']
        if not request.form['email_id']:
            return json_response(status="failed", error="Enter Email Id")
        else:
            email_id = request.form['email_id']
            try:
                cur = mysql.connection.cursor()
                query = cur.execute("SELECT history FROM user_profile WHERE email_id = %s", (email_id,))
                mysql.connection.commit()
                if query == 1:
                    result = cur.fetchall()
                    cur.close()
                    if result:
                        return json_response(status="success",history=result[0][0],email_id= email_id)
                    else:
                        return json_response(status="failed", error="No history")
                else:
                    return json_response(status="failed", error="Parameter values are not correct")
            except:
                return json_response(status="failed", error="SQL Error")
    except:
        return json_response(status="failed", error="Incomplete Parameters")


@app.route('/update_history', methods=['POST'])
def update_history():
    try:
        request.form['email_id'] and request.form['new_data']
        if not request.form['email_id']:
            return json_response(status="failed", error="Enter Email id")
        elif not request.form['new_data']:
            return json_response(status="failed", error="Empty saved")
        else:
            email_id = request.form['email_id']
            new_data = request.form['new_data']
            cur = mysql.connection.cursor()
            query = cur.execute("SELECT history FROM user_profile WHERE email_id = %s", (email_id,))
            mysql.connection.commit()
            if query == 1:
                result = cur.fetchall()
            # print(result[0][0])
                if result[0][0] == "null":
                    L = new_data
                else:
                    L= result[0][0]+"/"+new_data
                try:
                    other_query = cur.execute("UPDATE user_profile SET history=%s WHERE email_id=%s",(str( L), email_id,))
                    mysql.connection.commit()
                    if other_query==1:
                        return json_response(status="success")
                    else:
                        return json_response(status="failed", error="History have not updated")
                except (MySQL.Error, MySQL.Warning) as e:
                    return json_response(status="failed", error=e)
            else:
                return json_response(status="failed", error="No data")
            cur.close()
    except:
        return json_response(status="failed", error="Incomplete Parameters")


if __name__ == '__main__':
    app.debug = True
    app.run()
