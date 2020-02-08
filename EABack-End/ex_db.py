import os, time
from os import remove

from flask_security import roles_required
from xls2db import xls2db
import sqlite3
from flask import Flask, request, render_template, flash, send_from_directory, send_file
from Export import export
from Respaldo import respaldo
from config import app


# app = Flask(__name__)
# app.secret_key = '12345'

@roles_required('ADMINISTRADOR')
@app.route("/importation", methods=['GET', 'POST'])
def importation():
    backup_file = None
    if request.method == 'POST' and 'fileimported' in request.files and request.files['fileimported'].filename != '' \
            and str(request.form['tipo']) != '':

        file_ = request.files['fileimported']
        tipo_ = str(request.form['tipo'])
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
        file_.save(os.path.join(os.path.dirname(__file__), 'uploads', file_.filename))
        filsource = os.path.join(os.path.dirname(__file__), 'uploads', file_.filename)
        filtype = tipo_
        equery3 = equery4 = equery5 = equery6 = equery7 = """"""
        if filtype == 'Tipo ZAP Academy':
            condb = 'Ben_1.db'
            equery = """SELECT "NOMBRE", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "CURP", "CELULAR", "TELÉFONO CASA", 
                                    "CORREO"
                                    FROM data"""
            equery2 = """INSERT OR IGNORE INTO RECEIVERS ("given_name", "last_name", "s_last_name", "curp", "p_phone", "s_phone", 
                                        "email", "created_user") 
                                        VALUES (UPPER(?), UPPER(?), UPPER(?), ?, ?, ?, ?, 1)"""
        elif filtype == 'Tipo Apoyo a Mujeres':
            condb = 'Ben_2.db'
            equery = """SELECT "NOMBRE", "APELLIDO PATERNO", "APELLIDO MATERNO", "CURP", "CELULAR", "TELÉFONO CASA", 
                            ("CALLE"||" "||"NUMERO EXT") AS "DOMICILIO", "CÓDIGO"
                            FROM Beneficiarios """
            equery2 = """INSERT OR IGNORE INTO RECEIVERS ("given_name", "last_name", "s_last_name", "curp", "p_phone", "s_phone", 
                                "address", "zip_code", "created_user") 
                                VALUES (UPPER(?), UPPER(?), UPPER(?), ?, ?, ?, UPPER(?), ?, 1)"""
            equery3 = """UPDATE Beneficiarios SET `NUMERO EXT` = SUBSTR( `NUMERO EXT`, -2, -15)
                                    WHERE `NUMERO EXT` LIKE '%.0'"""
            equery4 = """UPDATE Beneficiarios SET CÓDIGO = SUBSTR( CÓDIGO, -2, -15) WHERE CÓDIGO LIKE '%.0'"""
            equery5 = """UPDATE Beneficiarios SET `TELÉFONO CASA` = SUBSTR( `TELÉFONO CASA`, -2, -15)
                            WHERE `TELÉFONO CASA` LIKE '%.0'"""
            equery6 = """UPDATE Beneficiarios SET CELULAR = SUBSTR( CELULAR, -2, -15) WHERE CELULAR LIKE '%.0'"""
        elif filtype == 'Tipo Jalisco te Reconoce':
            condb = 'Ben_3.db'
            equery = """SELECT "Nombre", "Primer Apellido", "Segundo Apellido", "CURP", "Celular", "Teléfono", 
                            ("Calle"||" "||"Numero Exterior"||" "||"Colonia") AS "Domicilio", "Código Postal", "Email"
                            FROM Hoja1 WHERE "Primer Apellido" <> ''"""
            equery2 = """INSERT OR IGNORE INTO RECEIVERS ("given_name", "last_name", "s_last_name", "curp", "p_phone", "s_phone", 
                                "address", "zip_code", "email", "created_user") 
                                VALUES (UPPER(?), UPPER(?), UPPER(?), ?, ?, ?, UPPER(?), ?, ?, 1)"""
            equery3 = """DELETE FROM Hoja1 WHERE `Primer Apellido` = ''"""
            equery4 = """UPDATE Hoja1 SET `Numero Exterior` = SUBSTR( `Numero Exterior`, -2, -15) WHERE 
                            `Numero Exterior` LIKE '%.0'"""
            equery5 = """UPDATE Hoja1 SET `Código Postal` = SUBSTR( `Código Postal`, -2, -15) WHERE `Código Postal` 
                            LIKE '%.0'"""
            equery6 = """UPDATE Hoja1 SET Teléfono = SUBSTR( Teléfono, -2, -15)
                             WHERE Teléfono LIKE '%.0'"""
            equery7 = """UPDATE Hoja1 SET Celular = SUBSTR( Celular, -2, -15) WHERE Celular LIKE '%.0'"""
        else:
            condb = 'Ben_4.db'
            equery = """SELECT "NOMBRE", "APELLIDO PATERNO", "APELLIDO MATERNO", "CURP", "CELULAR", "TELEFONO",
                                    "CORREO ELECTRONICO" FROM data1"""
            equery2 = """INSERT OR IGNORE INTO RECEIVERS ("given_name", "last_name", "s_last_name", "curp", "p_phone", "s_phone",
                                 "email", "created_user")
                                VALUES (UPPER(?), UPPER(?), UPPER(?), ?, ?, ?, ?, 1)"""

        def import_function():
            biter = "sqlitebiter -o " + condb + " file "
            excel = filsource
            cadena = biter + excel
            os.system(cadena)

        def import_funtion_2():
            xls2db(filsource, condb)

        if filtype == 'Tipo ZAP Academy':
            import_function()

        elif filtype == 'Tipo Apoyo a Mujeres':
            import_funtion_2()

        elif filtype == 'Tipo Jalisco te Reconoce':
            import_funtion_2()

        elif filtype == 'Otro Tipo':
            import_function()

        con = sqlite3.connect(condb)
        con2 = sqlite3.connect('zapiensa_project_v2.db')
        cur = con.cursor()
        cur2 = con2.cursor()

        if filtype == 'Tipo Apoyo a Mujeres':
            cur.execute(equery3)
            cur.execute(equery4)
            cur.execute(equery5)
            cur.execute(equery6)
        elif filtype == 'Tipo Jalisco te Reconoce':
            cur.execute(equery3)
            cur.execute(equery4)
            cur.execute(equery5)
            cur.execute(equery6)
            cur.execute(equery7)
        cur.execute(equery)

        monton = cur.fetchall()

        cur2.executemany(equery2, monton)
        con2.commit()
        con.close()
        con2.close()
        remove(condb)
        # return jsonify('Successful Transaction!')
        # flash("Transacción Exitosa!")
        os.remove(os.path.join(os.path.dirname(__file__), 'uploads', file_.filename))

    elif request.method == 'POST' and 'dir_target' in request.values and str(request.form['dir_target']) != '':
        export()

    elif request.method == 'POST' and 'dir_targetb' in request.values:
        respaldo()
        backup_file = respaldo()

    else:
        return 'algo no esta bien', 500

    return 'listo', 200


"""render_template('SU Exportaciones.html', una_lista=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                               'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           backup_file=backup_file, now=time.strftime("%Y%m%d-%H%M%S"))"""


@roles_required('ADMINISTRADOR')
@app.route("/exports", methods=['GET', 'POST'])
def exports():
    exportfile = export(request.args['filename'])
    return send_file(exportfile, as_attachment=True)


@roles_required('ADMINISTRADOR')
@app.route("/backup", methods=['GET', 'POST'])
def backup():
    #    file = respaldo()
    return send_file('zapiensa_project_v2.db',
                     attachment_filename='zapiensa_project_v2' + time.strftime("-%Y%m%d-%H%M%S") + '.db',
                     as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port='5003')
