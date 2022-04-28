from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from random import randint
import mysql.connector

mydb=mysql.connector.connect(host="projectdb.coe4avf23rbf.ap-south-1.rds.amazonaws.com", user="bankdbgroup", passwd="bdbcse202", database="test1" )
mycursor = mydb.cursor()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1)
app.secret_key = "bankDB"


# q=f"select * from customer  where c_id = 1050;"
# mycursor.execute(q)
# for i in mycursor:
#     for j in i:
#         print(j,end=" ")


# Login form
class LoginForm(FlaskForm):
    type = SelectField(u'Type', choices=[('c', 'Customer'), ('e', 'Employee'), ('a', 'Admin')])
    user = IntegerField("ID", validators=[DataRequired()])
    submit = SubmitField("Login")


# Home Page


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'logged_in' in session:
        q = f"SELECT * FROM customer WHERE c_id = {session['usr']};"
        mycursor.execute(q)
        customerDetails = mycursor.fetchone()
        return render_template("home.html", usr=session['usr'], type=session['type'], data=customerDetails)
    else:
        return render_template("home.html")


# Login page


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))

    cid = None
    form = LoginForm()

    if form.validate_on_submit():
        if form.type.data == "c":
            q = f"select c_id from customer where c_id = {form.user.data};"
            mycursor.execute(q)
            cid = mycursor.fetchone()
            if cid is None:
                return render_template("login.html", form=form, error="Invalid ID")
            else:
                session['usr'] = form.user.data
                session['type'] = "c"
                session['logged_in'] = True
                return redirect(url_for('home'))

        elif form.type.data == "e":
            # q = f"select e_id from employee where e_id = {form.user.data};"
            # mycursor.execute(q)
            # cid = mycursor.fetchone()
            # if cid is None:
            # 	return render_template("login.html", form=form)
            # else:
            session['usr'] = form.user.data
            session['type'] = "e"
            session['logged_in'] = True
            return redirect(url_for('home'))

        elif form.type.data == "a":
            # q = f"select a_id from admin where a_id = {form.user.data};"
            # mycursor.execute(q)
            # cid = mycursor.fetchone()
            # if cid is None:
            # 	return render_template("login.html", form=form)
            # else:
            session['usr'] = form.user.data
            session['type'] = "a"
            session['logged_in'] = True
            return redirect(url_for('home'))

    return render_template("login.html", form=form)


    # Logout page


@app.route("/logout", methods=["GET"])
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        session.pop('usr', None)
        session.pop('type', None)
        return render_template("logout.html", log=1)
    return render_template("logout.html")


    # @app.route("/Employee")
    # def Employee():
    # 	if 'usr' in session:
    # 		return render_template("Employee.html", data=session['usr'])
    #
    #

    # Account List
class AccountDetailsForm(FlaskForm):
	acc = SelectField(u'Choose account', coerce=int)
	submit = SubmitField("Update")


# Account Details
@app.route("/account", methods=["GET", "POST"])
def account():
	# will come here with a help of cid now ti show list of accounts in dropdown
	if 'logged_in' in session:
		c_id = session['usr']

		# can have multiple accounts -- show balance of each(need to be shown in a loop)
		#q = f"select * from accounts where account_no in (select account_no from customer_account where c_id= '{customer_id}');"

		q = f"select ca.c_id, a.account_no, a.balance, a.opening_date, " \
			f"a.closing_date,a.branch_id, ca.phone, ca.email, ca.is_primary " \
			f"from accounts a inner join customer_account ca on " \
			f"a.account_no = ca.account_no where ca.c_id = {c_id};"

		mycursor.execute(q)
		accountdetails = mycursor.fetchall()

		aid = 0
		curr_acc = accountdetails[aid]
		q = f"select * from debit_card where account_no={curr_acc[1]} and c_id ={c_id};"
		mycursor.execute(q)
		card = mycursor.fetchone()

		q = f"select * from upi where account_no = {curr_acc[1]};"
		mycursor.execute(q)
		upi = mycursor.fetchall()

		form = AccountDetailsForm()
		form.acc.choices = []

		for i in range(len(accountdetails)):
			form.acc.choices.append((i, accountdetails[i][1]))

		if form.validate_on_submit():
			aid = form.acc.data
			curr_acc = accountdetails[aid]

			q = f"select * from debit_card where account_no={curr_acc[1]} and c_id ={session['usr']};"
			mycursor.execute(q)
			card = mycursor.fetchone()

			q = f"select * from upi where account_no = {curr_acc[1]};"
			mycursor.execute(q)
			upi = mycursor.fetchall()

			return render_template("account.html", form=form, accountdetails=curr_acc, card=card, upi=upi)

		return render_template("account.html", form=form, accountdetails=curr_acc, card=card, upi=upi)

	else:
		return redirect(url_for('home'))


# class issuedata:
# 	def __init__(self, issuetype, content):
# 		self.issuetype=issuetype
# 		self.content=content
#
# 	def getissuetype(self):
# 		return self.issuetype
#
# 	def getcontent(self):
# 		return self.content

@app.route("/Customer/Support", methods= ["POST", "GET"])
def support():
	if 'logged_in' in session:
		c_id = session['usr']
		form = SupportQueriesForm()
		# for i in range(1, 9):
		# 	form.query.choices.append(i)
		form.query.choices = [1, 2, 3, 4, 5, 6, 7, 8]
		issues = {"Loans", "Debit Cards", "Credit Cards", "Fixed Deposits", "Recurring Deposits", "Payment issues", "Account issues", "Other"}
        if form.validate_on_submit():
            issue = form.query.data
            print(str(issue))
            if request.method == 'POST':
                content = request.form['content']
                q = f"select service_id from service"
                mycursor.execute(q)
				service_ids = mycursor.fetchall()
				no_of_ids = len(service_ids)
				q = f"insert into service(service_id, c_id, issue, s_date, e_id, resolved, issue) values(no_of_ids+1, c_id, issues[issue+1], '28-04-2022', 1, 0, content)"
				mycursor.execute(q)
				print(str(content))
				return redirect(url_for('issue'))
			return render_template("support.html", form=form)
		return render_template("support.html", form=form)
	else:
		return redirect(url_for('home'))


class SupportQueriesForm(FlaskForm):
	query = SelectField(u'Select the issue regarding your complaint', coerce=int)
	# desc = request.form.get('form-control')
	submit = SubmitField("Continue")


@app.route("/issue", methods= ["POST"])
def issue():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select * from service where c_id= {c_id};"
		mycursor.execute(q)
		issuedetails = mycursor.fetchall()
		print(issuedetails)
	return render_template("issue.html")


# Account List
class LoanDetailsForm(FlaskForm):
	ln = SelectField(u'Choose loan', coerce=int)
	submit = SubmitField("Update")


# Loans Page
@app.route("/loans", methods=["GET", "POST"])
def loans():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select b.loan_no, b.c_id, b.loan_id, l.loan_type, l.amount, l.duration, " \
			f"l.interest, l.emi, b.start_date, b.payments_remain, b.last_paid " \
			f"from borrow_loan b, loan l where b.loan_id = l.loan_id and b.c_id = {c_id};"
		mycursor.execute(q)
		loandetails = mycursor.fetchall()

		lid = 0
		curr_loan = loandetails[lid]

		q = f"select * from loan_payment where loan_no = {curr_loan[0]};"
		mycursor.execute(q)
		loanpayments = mycursor.fetchall()

		form = LoanDetailsForm()
		form.ln.choices = []

		for i in range(len(loandetails)):
			form.ln.choices.append((i, loandetails[i][0]))

		if form.validate_on_submit():
			lid = form.ln.data
			curr_loan = loandetails[lid]

			q = f"select * from loan_payment where loan_no = {curr_loan[0]};"
			mycursor.execute(q)
			loanpayments = mycursor.fetchall()
			print(loanpayments)

			return render_template("myloans.html", form=form, loandetails=curr_loan, loanpayments=loanpayments)

		return render_template("myloans.html", form=form, loandetails=curr_loan, loanpayments=loanpayments)
	else:
		return redirect(url_for('home'))


# @app.route("/Customer/Transactions")
# def Transactions():
# 	if 'usr' in session:
# 		customer_id = session['usr']['username']
#
# 		# 1.Bank
# 		q = f"select * from bank_transactions where sender = '{customer_id}' or receiver = '{customer_id}' ; "
# 		mycursor.execute(q)
# 		BankTransactionsdetails = mycursor.fetchall()
#
# 		# 2.Credit
# 		q = f"select * from cc_transactions where sender = '{customer_id}' or receiver = '{customer_id}' ; "
# 		mycursor.execute(q)
# 		CreditTransactionsdetails = mycursor.fetchall()
#
# 		# 3.Debit
# 		q = f"select * from dc_transactions where sender = '{customer_id}' or receiver = '{customer_id}' ; "
# 		mycursor.execute(q)
# 		DebitTransactionsdetails = mycursor.fetchall()
#
# 		# 4.UPI
# 		q = f"select * from upi_transactions where sender = '{customer_id}' or receiver = '{customer_id}' ; "
# 		mycursor.execute(q)
# 		UpiTransactionsdetails = mycursor.fetchall()
#
# 		# 5.Direct transactions
# 		q = f"select * from direct_transactions where sender = '{customer_id}' or receiver = '{customer_id}' ; "
# 		mycursor.execute(q)
# 		DirectTransactionsdetails = mycursor.fetchall()
#
# 		return render_template("Transactions.html", bank=BankTransactionsdetails, credit=CreditTransactionsdetails,
# 							   debit=DebitTransactionsdetails, upi=UpiTransactionsdetails,
# 							   direct=DirectTransactionsdetails, data=data)
#
#
# @app.route("/Customer/Editdetails", methods=["POST", "GET"])
# def CustomerEditdetails():
# 	if 'usr' in session:
# 		if request.method == 'POST':
# 			session['Cdetails'] = request.form
# 			print("session is of form ")
# 			print(session['Cdetails'])
#
# 			customer_id = session['usr']['username']
# 			fname = session['Cdetails']['first name']
# 			lname = session['Cdetails']['last name']
# 			dob = session['Cdetails']['DOB']
# 			sex = session['Cdetails']['Sex']
#
# 			q = f"UPDATE customer SET first_name = '{fname}', last_name = '{lname}',dob = '{dob}',sex = '{sex}' WHERE c_id = '{customer_id}' ; "
# 			mycursor.execute(q)
# 			mydb.commit()
# 			# Alter data here
# 			return redirect(url_for("Customer"))
#
# 		else:
# 			return render_template("CustomerEditdetails.html")



if __name__ == "main":
	app.run(debug=True)
