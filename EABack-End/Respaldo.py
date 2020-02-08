import os, time, shutil
from flask import Flask, request, app, render_template, flash
import sqlite3


def respaldo():

    error = None
    backup_file = None

    if request.method == 'POST' and 'dir_targetb' in request.values:
        print(backup_file)
        firststring = 'zapiensa_project_v2'
        file2_ = '.\\static\\'
        finalstring = firststring + ' ' + file2_
        backup_file = os.path.join(file2_, os.path.basename(firststring) +
                                   time.strftime("-%Y%m%d-%H%M%S") + '.db')
        print(backup_file)
        connection = sqlite3.connect(firststring)
        cursor = connection.cursor()

        # Lock database before making a backup
        cursor.execute('begin immediate')
        # Make new backup file
        shutil.copyfile(firststring + '.db', backup_file)
        print("\nCreating {}...".format(backup_file))
        # Unlock database
        connection.rollback()
        backup_file = os.path.basename(backup_file)
        # backup_file = "algo.txt"
        return backup_file


    else:
        flash('algo va mal!')
        error = 'datos no válidos!'
        print('nada')
    print(backup_file)

    # if request.method == 'GET':
    #    backup_file='algo'

    return render_template('SU Exportaciones.html', error=error, my_list=['Tipo ZAP Academy', 'Tipo Apoyo a Mujeres',
                                                                          'Tipo Jalisco te Reconoce', 'Otro Tipo'],
                           backup_file=backup_file)


