from celery import Celery
import subprocess
from subprocess import Popen,PIPE,STDOUT
import os
import re
import configparser
import json

app = Celery('tasks', backend='redis://localhost', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

@app.task
def lsl():
        return subprocess.check_output(['ls','-l'])

@app.task
def convert():
        out = subprocess.Popen(["timeout", "5m", "/usr/bin/pdf2swf", '-vv', '-T9', '-F', '/usr/share/fonts',
                '-p', '1', 'flight-school.pdf', '-o',
                'page1.swf'], stderr=STDOUT, stdout=PIPE)
        result = {}
        #result["stdout"] = out.communicate()[0]
        print(out.communicate()[0])
        result["returncode"] = out.returncode
        return json.dumps(result, ensure_ascii=False)
        #result = out.communicate()[0],out.returncode
        #return result

@app.task
def convertShapes():
        out = subprocess.Popen(["timeout", "5s", "/usr/bin/pdf2swf", '-vv', '-T9', '-F', '/usr/share/fonts',
                '-p', '1', 'plan_reseau_2008-2009.pdf', '-o',
                'page1.swf'], stderr=STDOUT, stdout=PIPE)
        str = unicode(out.communicate()[0], errors='ignore')
        result = str,out.returncode
        return result


@app.task
def convertTimeout():
        out = subprocess.Popen(["timeout", "5s", "/usr/bin/pdf2swf", '-vv', '-T9', '-F', '/usr/share/fonts',
                '-p', '1', 'sample-long-convert.pdf', '-o',
                'page1.swf'], stderr=STDOUT, stdout=PIPE)
        if type(out) is int:
                return "Command timed out", out
        else:
                result = out.communicate()[0],out.returncode
                return result

@app.task
def egrep(text):
        shapeCount = 0
        fontCount = 0
        drawCount = 0

        lines = text.splitlines()
        for line in lines:
                if re.search('shape id', line):
                        shapeCount += 1
                elif re.search('Updating font', line):
                        fontCount += 1
                elif re.search('Drawing', line):
                        drawCount += 1

        return shapeCount, fontCount, drawCount

@app.task
def cwd():
        cwd = os.getcwd()
        return cwd

@app.task
def getStatus():
        config = configparser.ConfigParser()
        config.read("config.ini")
        return config.get('SectionOne', 'Status')

