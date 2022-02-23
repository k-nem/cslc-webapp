import sqlite3
from flask import Flask, render_template, request, jsonify
from flask import g
import json

DATABASE = 'data/db.sqlite3'
app = Flask(__name__)

@app.route ('/')
def list():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from hymns_textblock where parent_block_id IS NULL or parent_block_id = 0")
    rows = cur.fetchall()
    con.commit()
    con.close()
    return render_template("home.html",rows = rows)


@app.route ('/texts', methods=['GET', 'POST'])
def texts():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from hymns_textblock where parent_block_id IS NULL or parent_block_id = 0")
    rows = cur.fetchall()
    con.commit()
    con.close()
    return render_template("texts.html",rows = rows)


@app.route ('/gloss')
def gloss():
    return render_template("glossary.html")

@app.route ('/about')
def about():
    return render_template("about.html")

@app.route ('/view/<num>', methods=['GET', 'POST'])
def view(num):
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    sqlcom = "select * from hymns_textblock where parent_block_id = " + str(num)
    cur.execute(sqlcom)
    rows = cur.fetchall()

    # breadcrumbs
    sqlt = "select * from hymns_textblock where id = " + str(num)
    cur.execute(sqlt)
    current = cur.fetchall()
    name = current[0][1]
    parentid = current[0][6]
    curlist = [num, name, parentid]

    i = parentid

    crumbs = []

    while i:
        psql = "select * from hymns_textblock where id = " + str(i)
        cur.execute(psql)
        pblock = cur.fetchall()

        if pblock:
            bid = pblock[0][0]
            name = pblock[0][1]
            pid = pblock[0][6]
            crumbs.append([bid, name, pid])
            i = pid

        else:
            break

    if crumbs:
        crumbs = sorted(crumbs, key=lambda x: x[0])

    if rows:
        return render_template("view.html", current =  curlist, crumbs = crumbs, rows = rows)

    if not rows:
        sqlcom = "select * from hymns_paragraph where parent_block_id = " + str(num)
        cur.execute(sqlcom)
        pars = cur.fetchall()

        return render_template("view.html",pars = pars, current =  curlist, crumbs = crumbs, rows = rows)

    con.commit()
    con.close()

@app.route ('/hymns/<num>', methods=['GET', 'POST'])
def hymns(num):
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    sqlcom = "select * from hymns_hymn where parent_id =" + str(num)
    cur.execute(sqlcom)
    hymns = cur.fetchall()

    # breadcrumbs
    sqlt = "select * from hymns_paragraph where id = " + str(num)
    cur.execute(sqlt)
    par = cur.fetchall()
    txt = par[0][1]
    order = par[0][3]
    parentid = par[0][4]
    curlist = [num, txt, order, parentid]

    i = parentid

    crumbs = []

    while i:
        psql = "select * from hymns_textblock where id = " + str(i)
        cur.execute(psql)
        pblock = cur.fetchall()

        if pblock:
            bid = pblock[0][0]
            name = pblock[0][1]
            pid = pblock[0][6]
            crumbs.append([bid, name, pid])
            i = pid

        else:
            break

    if crumbs:
        crumbs = sorted(crumbs, key=lambda x: x[0])



    con.commit()
    con.close()


    return render_template("hymns.html", current = curlist, crumbs = crumbs, hymns = hymns)

@app.route ('/hymn/<num>', methods=['GET', 'POST'])
def hymn(num):

    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # breadcrumbs
    crumbs = []
    i = num

    sqlt = "select * from hymns_hymn where id = " + str(i)
    cur.execute(sqlt)
    hym = cur.fetchall()
    txt = hym[0][2]
    order = hym[0][6] + 1
    parentid = hym[0][1]
    hlist = [i, txt, order, parentid]
    i = parentid

    cqlt = "select * from hymns_paragraph where id = " + str(i)
    cur.execute(cqlt)
    par = cur.fetchall()
    txt = par[0][1]
    order = par[0][3]
    parentid = par[0][4]
    curlist = [i, txt, order, parentid]
    i = parentid

    while i:
        psql = "select * from hymns_textblock where id = " + str(i)
        cur.execute(psql)
        pblock = cur.fetchall()
        if pblock:
            bid = pblock[0][0]
            name = pblock[0][1]
            pid = pblock[0][6]
            crumbs.append([bid, name, pid])
            i = pid

        else:
            break

    crumbs = sorted(crumbs, key=lambda x: x[0])


    simsql = "select * from hymns_similarities where hymn1_id =" + str(num)
    cur.execute(simsql)
    sim = cur.fetchall()
    ids = [[x['similarity_type'], x['hymn2_id']] for x in sim]
    # ids0 = [x[0], 0 for x in ids if x[1] == 0]
    # ids1 = [x[0], 1 for x in ids if x[1] == 1]
    # ids2 = [x[0], 2 for x in ids if x[1] == 2]
    # ids = [ids0, ids1, ids2]

    #ids0p = []

    idsp = {}

    ids0 = []
    ids1 = []
    ids2 = []

    for id in ids:
        # breadcrumbs
        crumbs = []
        i = id[1]
        type = id[0]

        sqlt = "select * from hymns_hymn where id = " + str(i)
        cur.execute(sqlt)
        hym = cur.fetchall()
        order = hym[0][6] + 1
        txt = hym[0][2]
        parentid = hym[0][1]
        hym = [i, order, parentid, txt]
        i = parentid

        cqlt = "select * from hymns_paragraph where id = " + str(i)
        cur.execute(cqlt)
        par = cur.fetchall()
        order = par[0][3]
        parentid = par[0][4]
        parag = [i, order, parentid]
        i = parentid

        while i:
            psql = "select * from hymns_textblock where id = " + str(i)
            cur.execute(psql)
            pblock = cur.fetchall()
            if pblock:
                bid = pblock[0][0]
                name = pblock[0][1]
                pid = pblock[0][6]
                crumbs.append([bid, name, pid])
                i = pid

            else:
                break

        crumbs = sorted(crumbs, key=lambda x: x[0])

        if type == 0:
            ids0.append([id, crumbs, parag, hym])

        elif type == 1:
            ids1.append([id, crumbs, parag, hym])

        elif type == 2:
            ids2.append([id, crumbs, parag, hym])

        else:
            continue

        idsp = {1: ids0, 2: ids1, 3: ids2}

    con.commit()
    con.close()

    return render_template("hymn.html", hlist = hlist, current = curlist, crumbs = crumbs, idsp = idsp)



if __name__ == "__main__":
    app.run(debug=True)
    list()
