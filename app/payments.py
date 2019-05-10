from flask import Blueprint, render_template, session, jsonify, abort, url_for, redirect, flash, request
from auth import login_required, flash_errors
import functools
from db import db, Teams, Players, Payments
from passlib.hash import bcrypt_sha256
import paypalrestsdk as paypal
from paypalrestsdk import *
import datetime
import os

payments_page = Blueprint('payment', __name__, url_prefix='/payment', template_folder='templates')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # TODO: We should be doing check_token for this routine
        if 'access_token' not in session:
            flash("You must be logged in to see that!", "error")
            return redirect(url_for('auth_page.signin'))

        return view(**kwargs)

    return wrapped_view

paypal.configure({
    "mode": "live",  # sandbox or live
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('CLIENT_SECRET')})


@payments_page.route('/paypal_payment', methods=['GET'])
@login_required
def paypal_payment():
    # Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'
    payment = paypal.Payment({
        "intent": "sale",

        # Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal"},

        # Redirect URLs
        "redirect_urls": {
            "return_url": "http://www.collegiatecounterstrike.com/payment/paypal_Return?success=true",
            "cancel_url": "http://www.collegiatecounterstrike.com/payment/paypal_Return?cancel=true"},

        # Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{

            # ItemList
            "item_list": {
                "items": [{
                    "name": "Summer League Fees",
                    "sku": "fee",
                    "price": "7.50",
                    "currency": "USD",
                    "quantity": 1}]},

            # Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": "7.5",
                "currency": "USD"},
            "description": "Summer League Fees"}]})

    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        for link in payment.links:
            if link.method == "REDIRECT":
                # Convert to str to avoid google appengine unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                redirect_url = str(link.href)
                print("Redirect for approval: %s" % (redirect_url))
                return redirect(redirect_url)
    else:
        print("Error while creating payment:")
        print(payment.error)
        return "Error while creating payment"

@payments_page.route('/paypal_Return', methods=['GET'])
def paypal_Return():
    player = Players.query.filter(Players.name == session.get('username')).first()
    # ID of the payment. This ID is provided when creating payment.
    paymentId = request.args['paymentId']
    payer_id = request.args['PayerID']
    payment = paypal.Payment.find(paymentId)

    # PayerID is required to approve the payment.
    if payment.execute({"payer_id": payer_id}):  # return True or False
        date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        player.paid = 'true'
        new_payment = Payments(session.get('username'), paymentId, payer_id, date)
        db.session.add(new_payment) 
        db.session.commit()
        flash("Payment executed successfully! Your transaction id is %s" % (payment.id), "success")
        return render_template("payments/payment.html")
    else:
        flash(payment.error, "error")
        return render_template("payments/payment.html")
    return render_template("payments/payment.html")

    

 

