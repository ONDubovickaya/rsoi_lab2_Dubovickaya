from quart import Quart
from payment.models.modelsClass import PaymentModel
from payment.interface.getPayment import getpaymentb
from payment.interface.postPayment import postpaymentb
from payment.interface.deletePayment import deletepaymentb
from payment.interface.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(getpaymentb)
app.register_blueprint(postpaymentb)
app.register_blueprint(deletepaymentb)
app.register_blueprint(healthcheckb)


def create_tables():
    PaymentModel.drop_table()
    PaymentModel.create_table()


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0',port=8050)