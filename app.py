from flask import Flask, render_template, request, session
import mysql.connector as mysql 
from flask_mail import Mail, Message
import random
import os

db=mysql.connect(
    host='localhost',
    user='root',
    password='#',
    database='#'
)

cur=db.cursor()

app=Flask(__name__)
app.secret_key="#"
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '#'
app.config['MAIL_PASSWORD'] = '#'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

IMG_FOLDER = os.path.join('static', 'IMG')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER
Flask_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'bank.png')

@app.route("/")
def Display_IMG():
    return render_template("registerac.html", user_image=Flask_Logo)

@app.route('/loginac')
def loginPage():
    return render_template('loginac.html', user_image=Flask_Logo)

@app.route('/deposit')
def DepositPage():
    return render_template('deposit.html', user_image=Flask_Logo)

@app.route('/withdraw')
def WithdrawPage():
    return render_template('withdraw.html', user_image=Flask_Logo)

@app.route('/transfer')
def TransferPage():
    return render_template('transfer.html', user_image=Flask_Logo)

@app.route('/checkbal')
def CheckBalPage():
    return render_template('checkbal.html', user_image=Flask_Logo)

@app.route('/delete')
def DeletePage():
    return render_template('delete.html', user_image=Flask_Logo)

@app.route('/registerac', methods=['POST'])
def registerData():
    acno=randN(5)
    f=request.form['fname']
    l=request.form['lname']
    m=request.form['mailid']
    u=request.form['uname']
    p=request.form['password']
    g=request.form['gender']
    a=request.form['add']
    amount=1000
    if f and l and m and u and p and g and a :
        session['acno']=acno
        session['uname']=u
        sql="SELECT user_name from bank_info where user_name=%s"
        un=[(session['uname'])]
        cur.execute(sql,un)
        account=cur.fetchone()
        sql1="SELECT acno from bank_info where acno=%s"
        un1=[(session['acno'])]
        cur.execute(sql1,un1)
        record=cur.fetchone()
        if account:
            if session['uname']==account[0]:
                return render_template('registerac.html',abc="UserName Already Exists!",user_image=Flask_Logo)
        elif record:
            if session['acno']==record[0]:
                return render_template('registerac.html',abc="AccountNo Already Exists!,Try Again",user_image=Flask_Logo)
        else:  
            storeData(acno,f,l,m,u,p,g,a,amount)  
            msg = Message('Account Created...', sender = 'noreply@demo.com', recipients = [m])
            msg.body = "Account Created Successful!!! Your Account No: {acno}, Username: {un}, Password{passw} and Initial Amount: {amount} ".format(acno=acno,amount=amount,un=u,passw=p)
            mail.send(msg)
            res="Account Created Successfully! Check Your Mail"
            return render_template('registerac.html',res=res,user_image=Flask_Logo)
    else:
        abc="All Fields are mandatory"
        return render_template('registerac.html',abc=abc,user_image=Flask_Logo)

@app.route('/loginac', methods=['GET','POST'])
def loginData():
    acno=request.form['acno']
    r=request.form['uname']
    p=request.form['password']
    global ac
    ac=acno
    if acno and r and p:
        session['acno']=acno
        session['uname']=r
        session['password']=p
        sql="SELECT acno,user_name,password from bank_info where acno=%s"
        val=[(session['acno'])]
        cur.execute(sql,val)
        account = cur.fetchone()
        if account:
            if  session['acno'] == str(account[0]) and session['uname'] == account[1] and session['password'] == account[2]:
                return render_template('success.html', user_image=Flask_Logo)
            else:
                result='Invalid Login'
                return render_template('loginac.html',result=result,user_image=Flask_Logo)
        else:
            result="No Records Found!! Please Create Account"
            return render_template('loginac.html',result=result,user_image=Flask_Logo)
    else:
        return render_template('loginac.html',result="All Fields are mandatory",user_image=Flask_Logo)

@app.route('/deposit', methods=['GET','POST'])
def deposit():
    acno=Storeacno()
    amount=request.form['amount']
    if acno and amount:
        session['acno']=acno
        session['amount']=amount
        sql="SELECT acno,amount from bank_info where acno=%s"
        val=[(session['acno'])]
        cur.execute(sql,val)
        account = cur.fetchone()
        if account:
            Addamount(account,session['amount'],session['acno'])
            return render_template('deposit.html',res="Successful Deposit!",user_image=Flask_Logo)
        else:
            return render_template('deposit.html',abc="No Account Found!",user_image=Flask_Logo)
    else:
        abc="All Fields are mandatory"
        return render_template('deposit.html',abc=abc,user_image=Flask_Logo)

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    acno=Storeacno()
    amount=request.form['amount']
    if acno and amount:
        session['acno']=acno
        session['amount']=amount
        sql="SELECT acno,amount from bank_info where acno=%s"
        val=[(session['acno'])]
        cur.execute(sql,val)
        account = cur.fetchone()
        if account:
            if account[1]>=int(session['amount']):
                Subamount(account,session['amount'],session['acno'])
                return render_template('withdraw.html',res="Successful Withdraw!",user_image=Flask_Logo)
            else:
                return render_template('withdraw.html',abc="Insufficient Balance!",user_image=Flask_Logo)
        else:
            return render_template('withdraw.html',abc="No Account Found!",user_image=Flask_Logo)
    else:
        abc="All Fields are mandatory"
        return render_template('withdraw.html',abc=abc,user_image=Flask_Logo)

@app.route('/transfer', methods=['GET','POST'])
def transfer():
    acno=Storeacno()
    frac=request.form['toacno']
    amount=request.form['amount']
    if frac and amount:
        session['acno']=acno
        session['toacno']=frac
        session['amount']=amount
        sql="SELECT acno,amount from bank_info where acno=%s"
        val=[(session['acno'])]
        cur.execute(sql,val)
        account = cur.fetchone()
        sql1="SELECT acno,amount from bank_info where acno=%s"
        val1=[(session['toacno'])]
        cur.execute(sql1,val1)
        record = cur.fetchone()
        if record:
            if account[0]==record[0]:
                return render_template('transfer.html',res="Successful Transfer!",user_image=Flask_Logo)
            else:
                if account[1]>=int(session['amount']):
                    Subamount(account,session['amount'],session['acno'])
                    Addamount(record,session['amount'],session['toacno'])
                    return render_template('transfer.html',res="Successful Transfer!",user_image=Flask_Logo)
                else:
                    return render_template('transfer.html',abc="Insufficient Balance!",user_image=Flask_Logo)
        else:
            return render_template('transfer.html',abc="No Reciever Account Found!",user_image=Flask_Logo)
    else:
        abc="All Fields are mandatory"
        return render_template('transfer.html',abc=abc,user_image=Flask_Logo)

@app.route('/checkbal', methods=['GET','POST'])
def checkbal():
    acno=Storeacno()
    session['acno']=acno
    sql="SELECT acno,amount from bank_info where acno=%s"
    val=[(session['acno'])]
    cur.execute(sql,val)
    account = cur.fetchone()
    if account:
        res="Balance in Your Account: Rs {amount}.00".format(amount=str(account[1]))
        return render_template('checkbal.html',res=res,user_image=Flask_Logo)
    else:
        return render_template('checkbal.html',abc="No Account Found!",user_image=Flask_Logo)

@app.route('/delete', methods=['GET','POST'])
def delete():
    acno=Storeacno()
    r=request.form['uname']
    p=request.form['password']
    if r and p:
        session['acno']=acno
        session['uname']=r
        session['password']=p
        sql="SELECT acno,user_name,password from bank_info where acno=%s"
        val=[(session['acno'])]
        cur.execute(sql,val)
        account = cur.fetchone()
        if account:
            if  session['acno'] == str(account[0]) and session['uname'] == account[1] and session['password'] == account[2]:
                sql="delete from bank_info where acno=%s"
                val=[(session['acno'])]
                cur.execute(sql,val)
                db.commit()
                res="Account Deleted Succesfully!"
                return render_template('loginac.html',res=res,user_image=Flask_Logo)
            else:
                result='Invalid Login'
                return render_template('delete.html',abc=result,user_image=Flask_Logo)
        else:
            result="No Records Found!! Please Create Account"
            return render_template('delete.html',abc=result,user_image=Flask_Logo)
    else:
        abc="All Fields are mandatory"
        return render_template('delete.html',abc=abc,user_image=Flask_Logo)

@app.route('/logout')
def logout():
    session.pop('acno')
    session.pop('uname')
    session.pop('password')
    return render_template('loginac.html', user_image=Flask_Logo)

def storeData(acno,first_name,last_name,mailid,user_name,password,gender,address,amount):
    sql="INSERT INTO bank_info(acno,first_name,last_name,mailid,user_name,password,gender,address,amount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val=(acno,first_name,last_name,mailid,user_name,password,gender,address,amount)
    cur.execute(sql,val)
    db.commit() 
def randN(N):
	min = pow(10, N-1)
	max = pow(10, N) - 1
	return random.randint(min, max)
def Storeacno():
    return ac
def Subamount(account,a,c):
    session['amount']=a
    session['acno']=c
    am=account[1]-int(session['amount'])
    sql="UPDATE bank_info SET amount=%s WHERE acno=%s"
    val=[str(am),session['acno']]
    cur.execute(sql,val)
    db.commit()
def Addamount(record,b,d):
    session['amount']=b
    session['toacno']=d
    am1=record[1]+int(session['amount'])
    sql="UPDATE bank_info SET amount=%s WHERE acno=%s"
    val=[str(am1),session['toacno']]
    cur.execute(sql,val)
    db.commit()

if __name__=="__main__":
    app.run(debug=True)