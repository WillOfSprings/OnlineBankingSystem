from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta, datetime
from random import randint
import mysql.connector

mydb=mysql.connector.connect(host="projectdb.coe4avf23rbf.ap-south-1.rds.amazonaws.com",user="bankdbgroup",passwd="bdbcse202", database="test1" )
mycursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = "bankDB"

# q=f"select * from customer  where c_id = 1050;"
# mycursor.execute(q)
# for i in mycursor:
#     for j in i:
#         print(j,end=" ")


@app.route("/", methods= ["POST", "GET"])
def home():
    if request.method == 'POST':
        session['usr'] = request.form
        print("session is of form ")
        print(session['usr'])
        
      
        if(request.form["Type"] == "Employee"):
            #print("Yessssssssssssssssssss")
            return redirect(url_for("Employee"))

        if(request.form["Type"] == "Customer"):
            return redirect(url_for("Customer"))

        if(request.form["Type"] == "Admin"):
            return redirect(url_for("Admin"))
    else:
        return render_template("home.html")


@app.route("/Employee")
def Employee():
    if 'usr' in session:
        return render_template("Employee.html",data=session['usr'])

@app.route("/Customer", methods= ["POST", "GET"])
def Customer():
    if 'usr' in session:
        print("not there yet.............")

        q=f"SELECT * FROM customer WHERE c_id= '{session['usr']['username']}';"
        mycursor.execute(q)
        customerDetails = mycursor.fetchall()



        return render_template("Customer.html",data=customerDetails)




@app.route("/Customer/Account")
def CustomerAccount():
    #will come here with a help of cid now ti show list of accounts in dropdown
    if 'usr' in session:
       

        customer_id = session['usr']['username']

        print("customer id is ")
        print(customer_id)
        
        #can have multiple accounts -- show balance of each(need to be shown in a loop)
        q=f"select * from accounts where account_no in (select account_no from customer_account where c_id= '{customer_id }');"
        mycursor.execute(q)
        accountdetails = mycursor.fetchall()

        # multiple credit cards ( can add pay for credit - cards )
        q=f"select * from debit_card where c_id = '{customer_id}' ;"
        mycursor.execute(q)
        debitcardDetails = mycursor.fetchall()

        q=f"select * from has_cc where c_id = '{customer_id}' ;"
        mycursor.execute(q)
        creditcardDetails = mycursor.fetchall()

        return render_template("CustomerAccount.html",data=accountdetails,dc = debitcardDetails,cc = creditcardDetails)


@app.route("/Customer/Transactions")
def Transactions():
    if 'usr' in session:
       

        customer_id = session['usr']['username']
        
        #1.Bank
        q=f"select * from bank_transactions where sender = '{customer_id }' or receiver = '{customer_id }' ; "
        mycursor.execute(q)
        BankTransactionsdetails = mycursor.fetchall()

        #2.Credit
        q=f"select * from cc_transactions where sender = '{customer_id }' or receiver = '{customer_id }' ; "
        mycursor.execute(q)
        CreditTransactionsdetails = mycursor.fetchall()

        #3.Debit
        q=f"select * from dc_transactions where sender = '{customer_id }' or receiver = '{customer_id }' ; "
        mycursor.execute(q)
        DebitTransactionsdetails = mycursor.fetchall()

        #4.UPI
        q=f"select * from upi_transactions where sender = '{customer_id }' or receiver = '{customer_id }' ; "
        mycursor.execute(q)
        UpiTransactionsdetails = mycursor.fetchall()

        #5.Direct transactions
        q=f"select * from direct_transactions where sender = '{customer_id }' or receiver = '{customer_id }' ; "
        mycursor.execute(q)
        DirectTransactionsdetails = mycursor.fetchall()
        
        return render_template("Transactions.html",bank=BankTransactionsdetails,credit=CreditTransactionsdetails,debit=DebitTransactionsdetails,upi=UpiTransactionsdetails,direct=DirectTransactionsdetails)



@app.route("/Customer/Editdetails", methods= ["POST", "GET"])
def  CustomerEditdetails():
    if 'usr' in session:
        if request.method == 'POST':
            session['Cdetails'] = request.form
            print("session is of form ")
            print(session['Cdetails'])

            customer_id = session['usr']['username']
            fname = session['Cdetails']['first name']
            lname = session['Cdetails']['last name']
            dob = session['Cdetails']['DOB']
            sex = session['Cdetails']['Sex']

            q = f"UPDATE customer SET first_name = '{fname}', last_name = '{lname}',dob = '{dob}',sex = '{sex}' WHERE c_id = '{customer_id}' ; "
            mycursor.execute(q)
            mydb.commit()
            # Alter data here
            return redirect(url_for("Customer"))
            
        else:
            return render_template("CustomerEditdetails.html")




if __name__ == "main":
    app.run(debug=True)


