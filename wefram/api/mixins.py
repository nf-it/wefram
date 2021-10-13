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
    sort_column: str = 'sort'

    @route('/reorder', methods=['PUT'])
    async def reorder(self, request: Request) -> NoContentResponse:
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

