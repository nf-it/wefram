from typing import *
from wefram import aaa, api, requests


# Place controllers and routes in this module.


# A couple examples are located below:
#
# @requests.route('/my_get_controller/{some_id}', methods=['GET'])
# async def my_get_controller(request: requests.Request) -> requests.Response:
#     some_id: str = request.path_params['some_id']
#     query_args: Dict[str, Union[str, List[str]]] = request.scope['query_args']
#
#     # some kind of work here :-)
#
#     return requests.JSONResponse({
#         'key1': 'value1',
#         'key2': 'value2'
#     })
#
#
# @requests.route('/my_post_controller/{some_id}', methods=['POST'])
# @aaa.requires('some_permission')
# async def my_post_controller(request: requests.Request) -> requests.Response:
#     some_id: str = request.path_params['some_id']
#     payload: Any = request.scope['payload']  # the payload (data) of the POST/PUT request
#
#     # some kind of work here :-)
#
#     return requests.NoContentResponse(204)


# A couple API controllers' examples are located below:

# @api.handle_get('/my_entity/{id}')
# @aaa.requires_authenticated()
# async def my_entity_get(request: requests.Request) -> requests.Response:
#
#     # some kind of work here :-)
#
#     return requests.PlainTextResponse("OK")
#
#
# @api.handle_post('/my_entity')
# @aaa.requires('some_permission')
# async def my_entity_post(request: requests.Request) -> requests.Response:
#
#     # some kind of work here :-)
#
#     return requests.NoContentResponse()

