from quart import Quart
from rental.models.modelsClass import RentalModel
from rental.interface.getRentals import getrentalsb
from rental.interface.getRental import getrentalb
from rental.interface.postRental import postrentalb
from rental.interface.deleteRental import deleterentalb
from rental.interface.postRentalFinish import postrentalbf
from rental.interface.healthCheck import healthcheckb

app = Quart(__name__)
app.register_blueprint(getrentalb)
app.register_blueprint(getrentalsb)
app.register_blueprint(postrentalb)
app.register_blueprint(deleterentalb)
app.register_blueprint(postrentalbf)
app.register_blueprint(healthcheckb)


def create_tables():
    RentalModel.drop_table()
    RentalModel.create_table()


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=8060)