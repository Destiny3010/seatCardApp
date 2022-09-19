# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from http.client import SWITCHING_PROTOCOLS
import string
from unittest import case
from pyramid.view import view_config

from mfplib.jobs.print import Printer, PaperSize, ColorMode

from mfplib.debug import Logger
from mfplib.app.storage import AppStorage
from mfplib.jobs.print import PrintJob
from mfplib.jobs.errors import (
    JobError,
    InvalidParameterError,
    PermissionError,
    QuotaEmptyError,
    RunningOtherServiceError,
    StorageFullError,
)

from .view import View

import csv
import chardet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm


# 正常
def Normal(canvas, name, company, font_size, font_color, *post):
    w,h = A4
    if font_color == "blue":
        canvas.setFillColorRGB(0, 0, 255) #蓝色
    elif font_color == "golden":
        canvas.setFillColorRGB(255, 215, 0) #金色
    else:
        canvas.setFillColorRGB(0, 0, 0) #黑色
    # 设置名字
    canvas.setFont("simhei", font_size)
    canvas.drawCentredString(0.5*w,0.28*h,name)
    # 设置公司
    canvas.setFont("simhei", 50)
    canvas.drawString(0.05*w,0.43*h,company)
    try:
        # 设置职务
        canvas.drawRightString(w-0.05*w,0.2*h,post[0])
    except:
        pass
# 倒置
def Inversion(canvas, name, company, font_size, font_color, *post):
    w,h = A4
    canvas.translate(w,h)
    canvas.scale(-1.0, -1.0)
    try:
        Normal(canvas, name, company, font_size, font_color, post[0])
    except:
        Normal(canvas, name, company, font_size, font_color)

# 读取CSV文件，输出CSV文件内容
def outputCSV(filename):
    with open(filename, 'rb') as File:
        text = File.read()   
    Encoding = chardet.detect(text)['encoding']
    csv_reader = csv.reader(open(filename,mode='r',encoding=Encoding))
    result = []
    for row in csv_reader:
        info = {}
        info['name'] = row[0]
        info['company'] = row[1]
        try: 
            info['post'] = row[2]
        except:
            pass
        result.append(info)
    result.pop(0)
    return result

# 读取CSV文件，生成PDF
def dealCSV(filename, font_size, font_color):
    pdfmetrics.registerFont(TTFont('simhei', 'simhei.ttf'))
    w,h = A4
    c = canvas.Canvas("documents/print.pdf", pagesize=A4)
    for row in outputCSV(filename):
        # 画出折痕线
        c.setDash([1,1,3,3,1,4,4,1], 0) #设置线条为点虚线
        c.line(0,0.5*h,w,0.5*h)
        c.line(0,0.85*h,w,0.85*h)
        c.line(0,0.15*h,w,0.15*h)
        try:    
            Normal(c,row['name'],row['company'], font_size, font_color, row['post'])
            Inversion(c,row['name'],row['company'], font_size, font_color, row['post'])
        except:
            Normal(c,row['name'],row['company'], font_size, font_color)
            Inversion(c,row['name'],row['company'], font_size, font_color)
        c.showPage()
    c.save()


class PrintView(View):
    """This class handles a print job request."""
    @view_config(route_name='print_jobs', request_method='POST', renderer='json')
    def start(self):
        """Starts a new print job."""
        # Get default print setting
        Logger.warn('接受到了请求！')
        printer = Printer(self.api_token)
        setting = printer.get_default_setting()
        
        # Configure print setting
        request_body = self.request.json_body
        setting.sets = int(request_body['sets'])
        setting.paper_size = PaperSize(request_body['paper_size'])
        setting.color_mode = ColorMode(request_body['color_mode'])
        setting.original_size_prioritized = False

        # Configure payload for background task
        font_size = int(request_body['font_size'])
        font_color = str(request_body['font_color'])
        Logger.warn('字号选择了' + str(font_size))
        Logger.warn('颜色选择了' + str(font_color))

        dealCSV("documents/zxk.csv", font_size, font_color)
    
        storage = AppStorage(self.api_token)

        try:
            PrintJob.start(self.api_token, setting, 'documents/print.pdf')
        except JobError as e:
            error_type = {
                InvalidParameterError: 'Invalid Parameter Error',
                PermissionError: 'Permission Error',
                QuotaEmptyError: 'Quota Empty Error',
                RunningOtherServiceError: 'Running Other Service Error',
                StorageFullError: 'Storage Full Error',
            }.get(type(e), 'Unexpected Error')
            Logger.error('打印任务不能启动的原因:"{}".'.format(error_type))
            Logger.error('Print job cannot be started by "{}".'.format(error_type))
        finally:
            storage.delete_file('documents/print.pdf')
            storage.delete_file('documents/zxk.csv')

        return self.response.ok()
