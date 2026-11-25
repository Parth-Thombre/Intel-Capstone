"""Outbound tool contract for tool-source and tool-destination transport.

ProcessTool and ToolHandshake remain domain data classes in
capstone.models.tool_handshake. This interface requests actions; asynchronous
observations provide readiness, authorization, collection and receipt evidence.
The additional event schemas and middleware wiring are future work.
"""

from abc import ABC, abstractmethod

from ..models.delivery_request import DeliveryRequest


class ProcessToolInterface(ABC):
    """A tool adapter boundary, separate from the ProcessTool data model.

    A method returning None means only that the call returned. It never proves
    readiness or physical completion. Implementations must report submission
    failures explicitly and publish correlated observations/results separately.
    Unimplemented operations must raise, rather than silently succeed.
    """

    @abstractmethod
    def request_pickup(self, request: DeliveryRequest) -> None:
        """Request release of request.bin at request.pickup_point.

        The source adapter must match the request's bin and tool point before
        reporting readiness. A tool source must not trigger gantry preparation.
        """
        raise NotImplementedError("Tool pickup requests are not implemented.")

    @abstractmethod
    def request_delivery(self, request: DeliveryRequest) -> None:
        """Request acceptance of request.bin at request.delivery_point.

        Destination readiness/authorization, completed transfer and receipt are
        separate observations. Calling this method must not mark a delivery done.
        """
        raise NotImplementedError("Tool delivery requests are not implemented.")
