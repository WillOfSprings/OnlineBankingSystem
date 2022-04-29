from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from random import randint
import mysql.connector

mydb = mysql.connector.connect(host="projectdb.coe4avf23rbf.ap-south-1.rds.amazonaws.com",
							   user="bankdbgroup",
							   passwd="bdbcse202",
							   database="bankdb")

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
	user = StringField("ID", validators=[DataRequired()])
	submit = SubmitField("Login")


# Home Page


@app.route('/', methods=['GET', 'POST'])
def home():
	if 'logged_in' in session:
		q = f"SELECT * FROM customer WHERE c_id = {session['usr']};"
		mycursor.execute(q)
		customerDetails = mycursor.fetchone()
		return render_template("home.html",
							   usr=session['usr'],
							   type=session['type'],
							   data=customerDetails)
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
		# q = f"select * from accounts where account_no in (select account_no from customer_account where c_id= '{customer_id}');"

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

			return render_template("account.html",
								   form=form,
								   accountdetails=curr_acc,
								   card=card,
								   upi=upi)

		return render_template("account.html",
							   form=form,
							   accountdetails=curr_acc,
							   card=card,
							   upi=upi)

	else:
		return redirect(url_for('home'))


# Loan List
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

			return render_template("myloans.html",
								   form=form,
								   loandetails=curr_loan,
								   loanpayments=loanpayments)

		return render_template("myloans.html",
							   form=form,
							   loandetails=curr_loan,
							   loanpayments=loanpayments)
	else:
		return redirect(url_for('home'))


@app.route("/applyloans", methods=["GET", "POST"])
def applyloans():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select * from loan;"
		mycursor.execute(q)
		availableloans = mycursor.fetchall()

		alid = None
		form = LoanDetailsForm()
		form.ln.choices = []

		for i in range(len(availableloans)):
			form.ln.choices.append((i, availableloans[i][0]))

		if form.validate_on_submit():
			alid = form.ln.data

		return render_template("applyloans.html", form=form, availableloans=availableloans)

	else:
		return redirect(url_for('home'))


# Deposit List
class DepDetailsForm(FlaskForm):
	dp = SelectField(u'Choose recurring deposit', coerce=int)
	submit = SubmitField("Update")


# Loans Page
@app.route("/deposits", methods=["GET", "POST"])
def deposits():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select * from fix_deposit where c_id = {c_id};"
		mycursor.execute(q)
		fixdetails = mycursor.fetchall()

		q = f"select * from rec_deposit where c_id = {c_id};"
		mycursor.execute(q)
		recdetails = mycursor.fetchall()

		rid = 0
		curr_rec = recdetails[rid]

		q = f"select * from deposit_record where rec_no = {curr_rec[0]};"
		mycursor.execute(q)
		recpayments = mycursor.fetchall()

		form = DepDetailsForm()
		form.dp.choices = []

		for i in range(len(recdetails)):
			form.dp.choices.append((i, recdetails[i][0]))

		if form.validate_on_submit():
			rid = form.dp.data
			curr_rec = recdetails[rid]

			q = f"select * from deposit_record where rec_no = {curr_rec[0]};"
			mycursor.execute(q)
			recpayments = mycursor.fetchall()

			return render_template("mydeps.html",
								   form=form,
								   fixdetails=fixdetails,
								   recdetails=curr_rec,
								   recpayments=recpayments)

		return render_template("mydeps.html",
							   form=form,
							   fixdetails=fixdetails,
							   recdetails=curr_rec,
							   recpayments=recpayments)
	else:
		return redirect(url_for('home'))


# Fix Deposit Form
class FixDepForm(FlaskForm):
	amount = IntegerField("Amount", validators=[
		DataRequired()])  # Can be done for selected values? same use for fix and rec deposit
	submit = SubmitField("Deposit")


# Fix deposit application page
@app.route("/fixdeposit", methods=["GET", "POST"])
def fixdeposit():
	if 'logged_in' in session:
		c_id = session['usr']
		form = FixDepForm()
		if form.validate_on_submit():
			amount = form.amount.data
			q = f"insert into fix_deposit values ({c_id}, {amount}, 0);"
			mycursor.execute(q)
			mydb.commit()
			return redirect(url_for('deposits'))
		return render_template("fixdeposit.html", form=form)

	else:
		return redirect(url_for('home'))


# Recurrence deposit select monthly pay from given values and insert


# Card List
class CardDetailsForm(FlaskForm):
	cc = SelectField(u'Choose card', coerce=int)
	submit = SubmitField("Update")


# Cards Page
@app.route("/cards", methods=["GET", "POST"])
def cards():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select hc.cc_no, hc.type_id, cc.card_name, cc.monthly_fee, cc.cc_limit," \
			f" hc.issue_date, hc.expiry, hc.cvv, hc.spent, hc.last_paid, hc.is_blocked " \
			f"from credit_card cc inner join has_cc hc on cc.type_id = hc.type_id where hc.c_id = {c_id};"
		mycursor.execute(q)
		carddetails = mycursor.fetchall()

		ccid = 0
		curr_cc = carddetails[ccid]

		q = f"select p_id, amount, cc_date, fined from cc_payment where cc_no = {curr_cc[0]};"
		mycursor.execute(q)
		ccpayment = mycursor.fetchall()

		form = CardDetailsForm()
		form.cc.choices = []

		for i in range(len(carddetails)):
			form.cc.choices.append((i, carddetails[i][0]))

		if form.validate_on_submit():
			ccid = form.cc.data
			curr_cc = carddetails[ccid]

			q = f"select p_id, amount, cc_date, fined from cc_payment where cc_no = {curr_cc[0]};"
			mycursor.execute(q)
			ccpayment = mycursor.fetchall()

			return render_template("mycc.html",
								   form=form,
								   carddetails=curr_cc,
								   ccpayment=ccpayment)

		return render_template("mycc.html",
							   form=form,
							   carddetails=curr_cc,
							   ccpayment=ccpayment)
	else:
		return redirect(url_for('home'))


# Card application page
@app.route("/cardapply", methods=["GET", "POST"])
def cardapply():
	if 'logged_in' in session:
		c_id = session['usr']
		q = f"select * from credit_card;"
		mycursor.execute(q)
		cardtypes = mycursor.fetchall()

		cardid = None
		form = CardDetailsForm()
		form.cc.choices = []

		for i in range(len(cardtypes)):
			form.cc.choices.append((i, cardtypes[i][0]))

		if form.validate_on_submit():
			cardid = form.cc.data

		# return render_template("mycc.html",
		# 					   form=form,
		# 					   carddetails=curr_cc,
		# 					   ccpayment=ccpayment)

		return render_template("mycc.html",
							   form=form,
							   carddetails=curr_cc,
							   ccpayment=ccpayment)

	else:
		return redirect(url_for('home'))


# Transaction select form
class TransactionForm(FlaskForm):
	tr = SelectField(u'Choose type', coerce=int)
	submit = SubmitField("Update")


@app.route("/transactions", methods=["GET", "POST"])
def transactions():
	if 'logged_in' in session and session['type'] == 'c':
		c_id = session['usr']
		trid = 1
		q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
			f"b.tr_timestamp, b.branch_id as trid, " \
			f"'Bank' as Type from bank_transactions b " \
			f"where sender = {c_id} or receiver = {c_id}  " \
			f"union " \
			f"select up.tr_id, up.sender, up.receiver, " \
			f"up.amount, up.tr_timestamp, up.upi_id as trid, " \
			f"'UPI' as Type from upi_transactions up " \
			f"where sender = {c_id}  or receiver = {c_id}  " \
			f"union " \
			f"select c.tr_id, c.sender, c.receiver, " \
			f"c.amount, c.tr_timestamp, c.cc_no as trid, " \
			f"'Credit Card' as Type from cc_transactions c " \
			f"where sender = {c_id}  or receiver = {c_id}  " \
			f"union select d.tr_id, d.sender, d.receiver, " \
			f"d.amount, d.tr_timestamp, d.dc_no as trid, " \
			f"'Debit Card' as Type from dc_transactions d " \
			f"where sender = {c_id} or receiver = {c_id}  " \
			f"union " \
			f"select dd.tr_id, dd.sender, dd.receiver, " \
			f"dd.amount, dd.tr_timestamp, 'Online' as trid, " \
			f"'Direct Transfer' as Type from direct_transactions dd " \
			f"where sender = {c_id}  or receiver = {c_id} ;"
		mycursor.execute(q)
		transactions = mycursor.fetchall()

		form = TransactionForm()
		form.tr.choices = [(1, 'All'), (2, 'Bank'),
						   (3, 'Debit Card'), (4, 'Credit Card'),
						   (5, 'UPI'), (6, 'Direct Transfer')]

		if form.validate_on_submit():
			trid = form.tr.data

			if trid == 1:
				q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
					f"b.tr_timestamp, b.branch_id as trid, " \
					f"'Bank' as Type from bank_transactions b " \
					f"where sender = {c_id} or receiver = {c_id}  " \
					f"union " \
					f"select up.tr_id, up.sender, up.receiver, " \
					f"up.amount, up.tr_timestamp, up.upi_id as trid, " \
					f"'UPI' as Type from upi_transactions up " \
					f"where sender = {c_id}  or receiver = {c_id}  " \
					f"union " \
					f"select c.tr_id, c.sender, c.receiver, " \
					f"c.amount, c.tr_timestamp, c.cc_no as trid, " \
					f"'Credit Card' as Type from cc_transactions c " \
					f"where sender = {c_id}  or receiver = {c_id}  " \
					f"union select d.tr_id, d.sender, d.receiver, " \
					f"d.amount, d.tr_timestamp, d.dc_no as trid, " \
					f"'Debit Card' as Type from dc_transactions d " \
					f"where sender = {c_id} or receiver = {c_id}  " \
					f"union " \
					f"select dd.tr_id, dd.sender, dd.receiver, " \
					f"dd.amount, dd.tr_timestamp, 'Online' as trid, " \
					f"'Direct Transfer' as Type from direct_transactions dd " \
					f"where sender = {c_id}  or receiver = {c_id} ;"
				mycursor.execute(q)
				transactions = mycursor.fetchall()


			elif trid == 2:
				q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
					f"b.tr_timestamp, b.branch_id as trid, " \
					f"'Bank' as Type from bank_transactions b " \
					f"where sender = {c_id} or receiver = {c_id};"
				mycursor.execute(q)
				transactions = mycursor.fetchall()

			elif trid == 3:
				q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
					f"b.tr_timestamp, b.dc_no as trid, " \
					f"'Debit Card' as Type from dc_transactions b " \
					f"where sender = {c_id} or receiver = {c_id};"
				mycursor.execute(q)
				transactions = mycursor.fetchall()

			elif trid == 4:
				q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
					f"b.tr_timestamp, b.cc_no as trid, " \
					f"'Credit Card' as Type from cc_transactions b " \
					f"where sender = {c_id} or receiver = {c_id};"
				mycursor.execute(q)
				transactions = mycursor.fetchall()

			elif trid == 5:
				q = f"select b.tr_id, b.sender, b.receiver, b.amount, " \
					f"b.tr_timestamp, b.upi_id as trid, " \
					f"'UPI' as Type from upi_transactions b " \
					f"where sender = {c_id} or receiver = {c_id};"
				mycursor.execute(q)
				transactions = mycursor.fetchall()

			elif trid == 6:
				q = f"select dd.tr_id, dd.sender, dd.receiver, " \
					f"dd.amount, dd.tr_timestamp, 'Online' as trid, " \
					f"'Direct Transfer' as Type from direct_transactions dd " \
					f"where sender = {c_id}  or receiver = {c_id} ;"
				mycursor.execute(q)
				transactions = mycursor.fetchall()



# Transfer form
class TransferForm(FlaskForm):
	tr = SelectField(u'Choose method', coerce=int)
	receiver = StringField('Receiver', validators=[DataRequired()])
	amount = DecimalField('Amount', validators=[DataRequired()])
	submit = SubmitField('Transfer')



# Transfer page
@app.route('/pay', methods=['GET', 'POST'])
def pay():
	if 'logged_in' in session and session['type'] == 'c':
		c_id = session['usr']
		payTo = None
		amount = None

		form = TransferForm()
		form.tr.choices = [(1, 'Debit Card'), (2, 'Credit Card'),
						   (3, 'UPI'), (4, 'Direct Transfer')]

		if form.validate_on_submit():
			payTo = form.receiver.data
			amount = form.amount.data
			trid = form.tr.data

			if trid == 1:
				pass

			elif trid == 2:
				pass

			elif trid == 3:
				chosenUpi = None
				q = f"select u.upi_id, a.account_no, ca.c_id " \
					f"from upi u inner join accounts a on " \
					f"u.account_no = a.account_no inner join " \
					f"customer_account ca on " \
					f"a.account_no = ca.account_no where ca.c_id = {c_id};"

				mycursor.execute(q)
				upidetails = mycursor.fetchall()

				form = UPITransferForm()
				form.upi.choice = []

				for i in range(len(upidetails)):
					form.upi.choices.append((i, upidetails[i][0]))

				if form.validate_on_submit():
					chosenUpi = upidetails[form.upi.data]


			elif trid == 4:
				chooseAcc = None
				q = f"select account_no from customer_account where c_id = {c_id};"
				mycursor.execute(q)
				acc = mycursor.fetchall()

				form = DirectTransferForm()
				form.acc.choices = []
				for i in range(len(acc)):
					form.acc.choices.append((i, acc[i][0]))

				if form.validate_on_submit():
					chooseAcc = form.acc.data
					# query for insert into direct transction
					# Trigger to update balance in both accounts



	else:
		return redirect(url_for('home'))


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
