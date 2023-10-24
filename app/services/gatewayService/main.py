from quart import Quart
from gateway.getCars import getcarsb
from gateway.getRentals import getrentalsb
from gateway.getRental import getrentalb
from gateway.postRentals import postrentalsb
from gateway.deleteRental import deleterentalb
from gateway.postRentalFinish import postrentalbf
from gateway.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(getcarsb)
app.register_blueprint(getrentalsb)
app.register_blueprint(postrentalsb)
app.register_blueprint(deleterentalb)
app.register_blueprint(postrentalbf)
app.register_blueprint(getrentalb)
app.register_blueprint(healthcheckb)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)