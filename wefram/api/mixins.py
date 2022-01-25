"""
Provides a set of mixins classes for Entity API. Using these mixins allow to
extend the default functionality with the standartized facilities.
"""

from typing import *
from dataclasses import dataclass
from ..requests import Request, NoContentResponse, HTTPException


__all__ = [
    'EntityAPIControllerRoute',
    'route',
    'SortedModelMixin'
]


@dataclass
class EntityAPIControllerRoute:
    path: str
    endpoint: Callable
    methods: List[Literal['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']]


def route(path: str, methods: Optional[List[str]] = None) -> Callable:
    """ A local (for mixins module) routing decorator. """

    def decorator(endpoint: Callable) -> EntityAPIControllerRoute:
        request_methods = methods or ['GET']
        if not isinstance(request_methods, (list, tuple)):
            request_methods = [request_methods, ]
        return EntityAPIControllerRoute(
            path=path,
            methods=request_methods,
            endpoint=endpoint
        )

    return decorator


class SortedModelMixin:
    """
    Add sorting functionality to the ModelAPI class. Routes the extra
    route for the API used to resort records by given sort indexes.
    """

    sort_column: str = 'sort'
    """ Defines which attribute of the Model to use for sorting. The
    value in this column will be updated when resorting.
    Default is ``'sort'``.
    """

    @route('/reorder', methods=['PUT'])
    async def reorder(self, request: Request) -> NoContentResponse:
        """ This route resorts records in the database using the defined
        ``sort_column`` attribute of this class.

        The frontend about to send payload as JSONed dict in the next
        format:

        ``
        {
            "object1_key": <sort_value>,
            "object2_key": <sort_value'>,
            ...
        }
        ``

        The controller takes all records from the corresponding database table
        (this controller uses the very simple approach without separating
        or using cursors), and reassigns their columns' values to the given
        sort values.

        For example, the frontend gives the next payload:

        ``
        {
            "1002": 100,
            "2054": 200
        }
        ``

        Basing on the example above, object with key (usually named ``id``)
        of "1002" will be updated, setting the sort to 100, and the object
        with key "2054" will get updated with sort to 200.
        """

        payload: dict = request.scope['payload']
        if not isinstance(payload, dict):
            raise HTTPException(400)
        model: ClassVar = getattr(self, 'model', None)
        instances: dict = {i.id: i for i in await model.all()}
        instance_id: Union[str, int]
        instance_sort: int
        for instance_id, instance_sort in payload.items():
            instance_id = instance_id
            instance_sort = int(instance_sort)
            if instance_id not in instances:
                continue
            await instances[instance_id].update(**{self.sort_column: instance_sort})
        return NoContentResponse(204)

