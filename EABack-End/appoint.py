import sqlite3
from config import app

@roles_required('ADMINISTRADOR')
@app.route("/appoint", methods=['GET', 'POST'])
def appointr():
    appoint()
    return 'done',200


def appoint():
    con = sqlite3.connect('zapiensa_project_v2.db')
    cur = con.cursor()
    paso1 = """CREATE TABLE COUNTS (conteo_general float, conteo_usuarios float, id_user int, 
                conteo_pendientes_usuario int)"""
    paso2 = """INSERT INTO COUNTS (conteo_general,conteo_usuarios,id_user, conteo_pendientes_usuario) VALUES ( (SELECT (
    SELECT count(id_receiver_event) FROM RECEIVERS_EVENTS WHERE id_receiver_event NOT IN (SELECT id_receiver_event FROM 
    FOLLOWS ))+(SELECT count(id_follow) FROM FOLLOWS WHERE notificated IS NULL)), (SELECT count(id_user) FROM USERS_ROLES 
    WHERE id_role<>1), (SELECT id_user FROM USERS_ROLES WHERE id_role<>1 LIMIT 1), (SELECT count(id_follow) FROM FOLLOWS 
    WHERE notificated IS NULL AND id_user=(SELECT id_user FROM USERS_ROLES WHERE id_role<>1 ORDER BY id_user LIMIT 1)) ) """
    paso3 = """INSERT INTO FOLLOWS (id_receiver_event, id_user) 
    SELECT a.id_receiver_event, b.id_user FROM RECEIVERS_EVENTS AS a, USERS AS b
    WHERE a.id_receiver_event NOT IN (SELECT id_receiver_event FROM FOLLOWS ) AND b.id_user=(SELECT id_user FROM COUNTS ORDER BY id_user DESC LIMIT 1) 
    LIMIT (CASE
        WHEN (SELECT (SELECT round((conteo_general/conteo_usuarios),0) FROM COUNTS ORDER BY id_user DESC LIMIT 1)>(SELECT conteo_pendientes_usuario FROM COUNTS ORDER BY id_user DESC LIMIT 1))
        THEN (SELECT (SELECT round((conteo_general/conteo_usuarios),0) FROM COUNTS ORDER BY id_user DESC LIMIT 1)-(SELECT conteo_pendientes_usuario FROM COUNTS ORDER BY id_user DESC LIMIT 1))
        ELSE 0
    END)"""
    paso4 = """INSERT INTO COUNTS (conteo_general,conteo_usuarios, id_user, conteo_pendientes_usuario) VALUES (
    (SELECT conteo_general-(round((conteo_general/conteo_usuarios),0)-conteo_pendientes_usuario)-conteo_pendientes_usuario FROM COUNTS ORDER BY id_user DESC LIMIT 1),
    (SELECT conteo_usuarios-1 FROM COUNTS ORDER BY id_user DESC LIMIT 1),
    (SELECT id_user+1 FROM COUNTS ORDER BY id_user DESC LIMIT 1),
    (SELECT count(id_follow) FROM FOLLOWS WHERE notificated IS NULL AND id_user=(SELECT id_user+1 FROM COUNTS ORDER BY id_user DESC LIMIT 1))
    )"""
    getvalue1 = """SELECT conteo_usuarios FROM COUNTS"""
    cur.execute(paso1)
    cur.execute(paso2)
    cur.execute(getvalue1)
    valor = cur.fetchone()
    valor1 = valor[0]

    while valor1 > 0:
        cur.execute(paso3)
        cur.execute(paso4)
        valor1 = valor1 - 1

    cur.execute("""DROP TABLE COUNTS""")

    con.commit()
    con.close()
