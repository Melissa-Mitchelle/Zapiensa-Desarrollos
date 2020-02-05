import sqlite3
import datetime
from sqlite3 import Error
from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from xlsxwriter.workbook import Workbook


def export():
    if request.method == 'POST':
        if 'dir_target' in request.values:
            file2_ = str(request.form['dir_target'])
            hnd = str(datetime.date.today())
            namebook = 'port'
            print(file2_)
            dirtarget2 = file2_ + "\Ex"
            xbook = dirtarget2 + namebook + hnd + '.xlsx'
            workbook = Workbook(xbook)
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': True, 'font_color': 'blue'})
            conn = sqlite3.connect('zapiensa_project_v2.db')
            c = conn.cursor()
            c.execute("SELECT * FROM view_receivers")
            mysel = c.execute("SELECT * FROM view_receivers")
            col_name_list = [tuple[0] for tuple in mysel.description]
            row = 0
            col = 0
            tp = 0

            for i in col_name_list:
                worksheet.write(row, col, col_name_list[tp], bold)
                col = col + 1
                tp = tp + 1

            rows = mysel.fetchall()

            for r, row in enumerate(rows):
                for c, col in enumerate(row):
                    worksheet.write(r + 1, c, col)

            workbook.close()
            conn.close()
