import os
import json
import datetime

from quart import Blueprint, Response, request
from .serviceOrders import get_data_from_service, post_data_from_service, delete_data_from_service

CARS_SERVICE_HOST = os.environ['CARS_SERVICE_HOST']
CARS_SERVICE_PORT = os.environ['CARS_SERVICE_PORT']
RENTAL_SERVICE_HOST = os.environ['RENTAL_SERVICE_HOST']
RENTAL_SERVICE_PORT = os.environ['RENTAL_SERVICE_PORT']
PAYMENT_SERVICE_HOST = os.environ['PAYMENT_SERVICE_HOST']
PAYMENT_SERVICE_PORT = os.environ['PAYMENT_SERVICE_PORT']

def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['wrong']

    errors = []
    if 'carUid' not in body or type(body['carUid']) is not str or \
            'dateFrom' not in body or type(body['dateFrom']) is not str or \
            'dateTo' not in body or type(body['dateTo']) is not str:
        return None, ['wrong structure']

    return body, errors


def clear_headers(headers: dict) -> dict:
    technical_headers = ['Remote-Addr', 'User-Agent', 'Accept', 'Postman-Token', 'Host', 'Accept-Encoding',
                         'Connection']
    keys = list(headers.keys())
    for key in keys:
        if key in technical_headers:
            del headers[key]

    return headers

postrentalsb = Blueprint('post_rentals', __name__, )

@postrentalsb.route('/api/v1/rental/', methods=['POST'])
async def post_rentals() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps({
                'errors': ['wrong user name']
            })
        )

    body, errors = validate_body(await request.body)
    if len(errors) > 0:
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps(errors)
        )
    """
    if 'X-User-Name' not in request.headers:
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps({"errors": ["wrong user name"]})
        )
    
    body = await request.get_json()
    if not body or 'carUid' not in body or 'dateFrom' not in body or 'dateTo' not in body:
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps({"errors": ["wrong structure"]})
        )
    """
    car_order_url = f"http://{CARS_SERVICE_HOST}:{CARS_SERVICE_PORT}/api/v1/cars/{body['carUid']}/order"
    car_order_response = get_data_from_service(car_order_url, timeout=5)
    
    if car_order_response is None:
        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({"errors": ["service not working"]})
        )

    if car_order_response.status_code == 404 or car_order_response.status_code == 403:
        return Response(
            status=car_order_response.status_code,
            content_type='application/json',
            response=car_order_response.text
        )

    car = car_order_response.json()
    price = (datetime.datetime.strptime(body['dateTo'], "%Y-%m-%d").date() - datetime.datetime.strptime(body['dateFrom'], "%Y-%m-%d").date()).days * car['price']

    payment_url = f"http://{PAYMENT_SERVICE_HOST}:{PAYMENT_SERVICE_PORT}/api/v1/payment/"
    payment_response = post_data_from_service(payment_url, timeout=5, json={"price": price})

    if payment_response is None:
        rollback_url = f"http://{CARS_SERVICE_HOST}:{CARS_SERVICE_PORT}/api/v1/cars/{body['carUid']}/order"
        delete_data_from_service(rollback_url, timeout=5)

        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({"errors": ["service not working"]})
        )

    payment = payment_response.json()
    body['paymentUid'] = payment['paymentUid']

    rental_url = f"http://{RENTAL_SERVICE_HOST}:{RENTAL_SERVICE_PORT}/api/v1/rental/"
    rental_response = post_data_from_service(rental_url, timeout=5, json=body, headers={'X-User-Name': request.headers['X-User-Name']})

    if rental_response is None:
        rollback_url = f"http://{CARS_SERVICE_HOST}:{CARS_SERVICE_PORT}/api/v1/cars/{body['carUid']}/order"
        delete_data_from_service(rollback_url, timeout=5)

        rollback_url = f"http://{PAYMENT_SERVICE_HOST}:{PAYMENT_SERVICE_PORT}/api/v1/payment/{body['paymentUid']}"
        delete_data_from_service(rollback_url, timeout=5)

        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({"errors": ["service not working"]})
        )

    if rental_response.status_code != 200:
        return Response(
            status=rental_response.status_code,
            content_type='application/json',
            response=rental_response.text
        )

    rental = rental_response.json()

    rental['payment'] = payment
    del rental['paymentUid']

    return Response(
        status=200,
        content_type='application/json',
        response=json.dumps(rental)
    )
"""
def validate_body(body):
    try:
        body = json.loads(body)
    except:
        return None, ['wrong']

    errors = []
    if 'carUid' not in body or type(body['carUid']) is not str or \
            'dateFrom' not in body or type(body['dateFrom']) is not str or \
            'dateTo' not in body or type(body['dateTo']) is not str:
        return None, ['wrong structure']

    return body, errors


def clear_headers(headers: dict) -> dict:
    technical_headers = ['Remote-Addr', 'User-Agent', 'Accept', 'Postman-Token', 'Host', 'Accept-Encoding',
                         'Connection']
    keys = list(headers.keys())
    for key in keys:
        if key in technical_headers:
            del headers[key]

    return headers


@postrentalsb.route('/api/v1/rental/', methods=['POST'])
async def post_rentals() -> Response:
    if 'X-User-Name' not in request.headers.keys():
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps({
                'errors': ['wrong user name']
            })
        )

    body, errors = validate_body(await request.body)
    if len(errors) > 0:
        return Response(
            status=400,
            content_type='application/json',
            response=json.dumps(errors)
        )

    response = post_data_from_service(
        'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
        + '/api/v1/cars/' + body['carUid'] + '/order', timeout=5)

    if response is None:
        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({
                'errors': ['service not working']
            })
        )
    if response.status_code == 404 or response.status_code == 403:
        return Response(
            status=response.status_code,
            content_type='application/json',
            response=response.text
        )

    car = response.json()
    price = (datetime.datetime.strptime(body['dateTo'], "%Y-%m-%d").date() - \
            datetime.datetime.strptime(body['dateFrom'], "%Y-%m-%d").date()).days * car['price']

    response = post_data_from_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT']
        + '/api/v1/payment/', timeout=5, data={'price': price})

    if response is None:
        response = delete_data_from_service(
            'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
            + '/api/v1/cars/' + body['carUid'] + '/order', timeout=5)

        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({
                'errors': ['service not working']
            })
        )

    payment = response.json()
    body['paymentUid'] = payment['paymentUid']

    response = post_data_from_service(
        'http://' + os.environ['RENTAL_SERVICE_HOST'] + ':' + os.environ['RENTAL_SERVICE_PORT']
        + '/api/v1/rental/', timeout=5, data=body, headers={'X-User-Name': request.headers['X-User-Name']})

    if response is None:
        response = delete_data_from_service(
            'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
            + '/api/v1/cars/' + body['carUid'] + '/order', timeout=5)
        response = delete_data_from_service(
            'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT']
            + '/api/v1/payment/' + body['paymentUid'], timeout=5)
        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({
                'errors': ['service not working']
            })
        )

    if response.status_code != 200:
        return Response(
            status=response.status_code,
            content_type='application/json',
            response=response.text
        )

    rental = response.json()

    rental['payment'] = payment
    del rental['paymentUid']

    return Response(
        status=200,
        content_type='application/json',
        response=json.dumps(rental)
    )
    """
