from fileinput import filename
from fpdf import FPDF
from flask import Flask, render_template, request
import pickle
import numpy as np
import pyautogui
from geopy.geocoders import Nominatim
import webbrowser
from time import sleep
from PIL import Image
from itertools import product
import os
import matplotlib.image as image
import cv2
import numpy
import win32clipboard
import sys
import shutil
from operator import index
import glob
from flask import * 
from flask_mysqldb import MySQL
import pdfkit

# ADMIN LOGIN CREDENTIALS
email="kp@gmail.com"
pwd="1234"


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Keerthi*1'
app.config['MYSQL_DB'] = 'bridgeDB'
app.config['MYSQL_CURSORCLASS']='DictCursor'
inp=""

mysql = MySQL(app)
 
def detect(file):
    os.chdir(r'yolov5')
    os.system(f"python detect.py --weights runs/train/exp/weights/best.pt --img 640 --conf 0.25 --source {file} --save-txt")


def choose():
    with open('convert.txt', 'r') as f:
        lines = f.readlines()
    # print(lines)
    mainlst=[]
    for i in lines:
        if i=="\n":
            continue
        else:
            lst=[]
            temp=i.split(',')
            for k in temp:
                temp2=k.split(':')
                if("\n" in temp2[-1]):
                    continue
                else:
                    lst.append(int(temp2[-1]))
            mainlst.append(int(lst[1])+int(lst[2])+int(lst[3]))
    ind=mainlst.index(max(mainlst))+1
    i = 0
    file_name = r"static\patchedimages"
    for filename in glob.glob(file_name + "/*.jpg"):
        i += 1
        if i == ind:
            im = Image.open(filename)
            im.save(r'static\file name2.jpg')
    return ""

#.....................................

def finalresult(file):
    with open(file) as f:
        lines = f.readlines()
    dic = {"waterbodys": 0, "facilitiess": 0,
       "roadnetworks": 0, "habitations": 0, "bridges": 0}
    
    for line in lines:
        if line[0] == "4":
            dic["waterbodys"] += 1
        if line[0] == "1":
            dic["facilitiess"] += 1
        if line[0] == "3":
            dic["roadnetworks"] += 1
        if line[0] == "2":
            dic["habitations"] += 1
        if line[0] == "0":
            dic["bridges"] += 1
    # if(dic["waterbodys"]==0):
    #     return "no waterbody!!"
    if dic["bridges"]!=0:
        im = Image.open(file)
        os.remove(os.path.join(r"static\patchedimages",f'{im}'))
    with open('convert.txt', 'a') as convert_file:
        convert_file.write(json.dumps(dic)) 
        convert_file.write("\n")
    x = dic["facilitiess"]+dic["habitations"]+dic["roadnetworks"]
    with open('output1.txt', 'a') as fp:
        fp.write(str(x))
        fp.write("\n")
    return " "

def labelling(imag):
    img = image.imread(imag)
    lower_blue = numpy.array([110, 50, 50])
    upper_blue = numpy.array([160, 255, 255])
    l = [156, 192, 250]
    l1 = []
    cnt1 = 0
    cnt2 = 0
    for i in img:
        l2 = []
        for j in i:
            temp = 0
            if(lower_blue[0] <= j[0] and upper_blue[0] >= j[0]):
                temp += 1
            if(lower_blue[1] <= j[1] and upper_blue[1] >= j[1]):
                temp += 1
            if(lower_blue[2] <= j[2] and upper_blue[2] >= j[2]):
                temp += 1
            if temp == 3:
                cnt1 += 1
                l2.append(2)
            else:
                cnt2 += 1
                l2.append(0)
        l1.append(l2)
    print(cnt1)
    print(cnt2)    
    # with open(r'output.txt', 'w') as fp:
    #     for item in l1:
    #         # write each item on a new line
    #         fp.write("%s\n" % item)
    #     # print('Done')
    filename_csv = f'{imag}'

    if(cnt1 < 8000 or cnt1 > 40000 or cnt2 == 0 or cnt1 == 0):
        print("inside if condition")
        os.remove(os.path.join(r"static\patchedimages",f'{imag}'))
    return l1

@app.route('/')
def man():
    # return render_template('index.html')
    return render_template('home.html')


@app.route('/home', methods=['POST','GET'])
def home():
    # data1 = request.form['a']
    # arr = np.array([[data1, data2, data3, data4]])
    # pred = model.predict(arr)
    # return render_template('after.html', data=pred)
    return render_template('home.html')

@app.route('/search', methods=['POST','GET'])
def search():
    return render_template('search.html')

@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

# @app.route('/maps')
# def maps():
#     let_url="https://www.google.com/maps/"
#     webbrowser.open(let_url)
#     sleep(10)
#     # get clipboard data
#     win32clipboard.OpenClipboard()
#     data = win32clipboard.GetClipboardData()
#     win32clipboard.CloseClipboard()
#     x=data.split(',')
#     lat=x[0]
#     lon=x[1]



@app.route('/usercomplaint', methods = ['POST', 'GET'])
def usercomplaint():
    if request.method == 'POST':
        try:
            firstName = request.form['fname']
            phoneno = request.form['phone']
            state = request.form['statename']
            let_url="https://www.google.com/maps/"
            webbrowser.open(let_url)
            sleep(10)
            # get clipboard data
            pyautogui.hotkey('ctrl', 'w')
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            x=data.split(',')
            lat=x[0]
            lon=x[1]
            # try:
            motivation = request.form['mot']
            req_value='No'
            cur = mysql.connection.cursor()
        
            query="update states set count=count+1 where statename=%s"
            cur.execute(query,(state,))
            mysql.connection.commit()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT CONCAT(stateid,count) as id FROM states where statename=%s",(state,))
            tempid = cur.fetchall()
            id=tempid[0]['id']

            query="INSERT INTO usercomplaints(id,name,phoneno,latitude,longitude,state,motivation,req_value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query,(id,firstName,phoneno,lat,lon,state,motivation,req_value))
            mysql.connection.commit()
            cur.close()
            msg="Thank you for filling!"
            return render_template('home.html',msg=msg,displaydata=data)
        except:
            #pyautogui.hotkey('ctrl', 'w')
            error="Enter the details correctly!"
            return render_template('complaint.html',error=error)


@app.route('/display', methods = ['GET', 'POST'])
def display():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usercomplaints")
    data = cur.fetchall()
    return render_template('display.html',displaydata=data)

@app.route('/adminlogin', methods=['POST','GET'])
def adminlogin():
    if request.method=='POST':
        uname=request.form["username"]
        password=request.form["password"]
        if(uname==email and password==pwd):
            return redirect(url_for('display'))
        else:
            return render_template('login.html',error="Invalid login!")
    return render_template('login.html')

@app.route('/aboutus', methods=['POST','GET'])
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus', methods=['POST','GET'])
def contactus():
    return render_template('contactus.html')

@app.route('/submitform', methods=['POST','GET'])
def submitform():
    return render_template('submit.html')



def next():
    file_name = r"static\patchedimages"
    for file in glob.glob(file_name + "/*.jpg"):
        detect(file)
    return "nothing"

@app.route('/prediction')
def tile():
    filename=r'static\file name1.jpg'
    d=271
    name, ext = os.path.splitext(filename)
    img = Image.open(filename)
    w, h = img.size

    grid = product(range(0, h-h % d, d), range(0, w-w % d, d))
    newname = r'static\\patchedimages\\image'
    for k, j in grid:
        box = (j, k, j+271, k+271)
        out = os.path.join(r'static\\patchedimages', f'{newname}{k}{j}{ext}')
        img.crop(box).save(out)

    file_name = r"static\patchedimages"
    for filename in glob.glob(file_name + "/*.jpg"):
        labelling(filename)


    next()


    a=os.listdir(r"static\patchedimages")
    #print(len(a)) contains the number of images
    b=os.listdir(r"yolov5\runs\detect")
    #print(len(b)) contains the total number of runs 
    from pathlib import Path
    directory = r"yolov5\runs\detect"
    files = Path(directory).glob('*')
    cnt=0
    for file in files:
        file=str(file)
        file+="\labels"
        for file1 in glob.glob(file + "/*.txt"):
            finalresult(file1)
            cnt=cnt+1
    choose()
    with open("output1.txt",'w') as file:
        pass

    #......DELETING THE FILES.........

    directory = r"yolov5\runs\detect"
    files = Path(directory).glob('*')
    for file in files:
        print(file)
        shutil.rmtree(file)
    #........................................

    img_names=[]
    images=os.listdir(r"static\patchedimages")
    link="abcd"
    return render_template("final1.html",cnt=cnt,images=images,link=link)


@app.route('/bestpatch')
def bestpatch():
    with open('convert.txt', 'r') as f:
        lines = f.readlines()
    # print(lines)
    mainlst=[]
    templst=[]
    for i in lines:
        if i=="\n":
            continue
        else:
            lst=[]
            temp=i.split(',')
            for k in temp:
                temp2=k.split(':')
                if("\n" in temp2[-1]):
                    continue
                else:
                    lst.append(int(temp2[-1]))
            mainlst.append(int(lst[1])+int(lst[2])+int(lst[3]))
            templst.append(lst)
    ind=mainlst.index(max(mainlst))
    facilities=templst[ind][1]
    roadnetwork=templst[ind][3]
    habitation=templst[ind][2]
    k=0
    with open('convert.txt', 'w') as f:
        pass
    

    return render_template('final1.html',facilites=facilities,roadnetwork=roadnetwork,habitation=habitation)

@app.route('/result/')
def output():
    global inp
    inp = request.args.get("id")
    
    cur = mysql.connection.cursor()
    try:
        query="SELECT latitude,longitude from usercomplaints where id=%s"
        cur.execute(query,(inp,))
        temp=cur.fetchall()
        print(temp)
        lat=temp[0]['latitude']
        lon=temp[0]['longitude']
        let_url="https://www.google.com/maps/@?api=1&map_action=map&center="+str(lat)+"%2C"+str(lon)+"&zoom=15"
        webbrowser.open(let_url)  # Go to example.com
        sleep(3) 
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'static\file name1.jpg')
        img=Image.open(r'static\file name1.jpg')
        pyautogui.hotkey('ctrl', 'w')
        w,h=img.size

        left = 210
        top = 150
        right = 1710
        bottom = 965

        img = img.crop( (left, top, right, bottom) ) # previously, image was 826 pixels wide, cropping to 825 pixels wide
        img.save(r'static\file name1.jpg')
        return render_template('output.html')
    except:
        error="Please enter a valid ID"
        return render_template('display.html',error=error)

@app.route('/printpdf',methods=['POST'])
def printpdf():
    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread(r'static\file name2.jpg')
    large_image = cv2.imread(r'static\file name1.jpg')
    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    MPx,MPy = mnLoc
    trows,tcols = small_image.shape[:2]
    cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
    im = Image.fromarray(large_image)
    im.save(r"static\outlined_image.jpg")
    cur = mysql.connection.cursor()
    query="update usercomplaints set req_value='Yes' where id=%s"
    cur.execute(query,(inp,))
    mysql.connection.commit()
    cur.close()
    # return redirect(url_for('display'))
    return redirect(url_for('printpdf1'))

@app.route('/printpdf1')
def printpdf1():
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Times", size = 15)
    pdf.rect(10,10,190,275)

    # pdf.image(r"https://rural.nic.in/sites/all/themes/rural/images/emblem-dark.png",20,20,120,90,'PNG') 
    pdf.cell(0,20, txt = "MINISTRY OF RURAL DEVELOPMENT",ln = 1, align = 'C')
    pdf.cell(0,10, txt = "BRIDGE REPORT",ln = 2, align = 'C')
    pdf.cell(0,15,txt="Original Image of the location specified by the user",ln=3,align='C')

    pdf.image(r"static\file name1.jpg",50,55,120,90,'JPG')

    pdf.cell(0,200,txt="Best patch to lay a bridge on",ln=4,align="C")

    pdf.image(r"static\file name2.jpg",50,160,120,90,'JPG')

    pdf.add_page()

    pdf.set_font("Times", size = 15)
    pdf.rect(10,10,190,275)
    pdf.cell(0,20,txt="The best patch outlined in the original image",ln=1,align='C')

    pdf.image(r"static\outlined_image.jpg",50,30,120,90,'JPG')

    pdf.output(r"report.pdf")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usercomplaints")
    data = cur.fetchall()
    return render_template('display.html',report="msg",displaydata=data)


if __name__ == "__main__":
    app.run(debug=True)

    
