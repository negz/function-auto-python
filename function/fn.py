"""A Crossplane composition function."""

import grpc

from function import sdk
from function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from function.proto.v1beta1 import run_function_pb2_grpc as grpcv1beta1


class FunctionRunner(grpcv1beta1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = sdk.get_logger()

    async def RunFunction(  # noqa:N802 # This is the interface gRPC generates.
        self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1beta1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = sdk.response_from(req)

        for name, dr in rsp.desired.resources.items():
            log = log.bind(composed_resource_name=name)

            # If this desired resource doesn't exist in the observed resources,
            # it can't be ready because it doesn't exist yet.
            if name not in req.observed.resources:
                log.debug(
                    "Ignoring desired resource that does not appear in "
                    "observed resources"
                )
                continue

            if dr.ready != fnv1beta1.READY_UNSPECIFIED:
                log.debug(
                    "Ignoring desired resource that already has explicit readiness",
                    ready=dr.ready,
                )
                continue

            log.debug("Found desired resource with unknown readiness")

            condition = sdk.get_condition(
                req.observed.resources[name].resource, "Ready"
            )

            if condition.status == "True":
                log.info("Automatically determined that composed resource is ready")
                dr.ready = fnv1beta1.READY_TRUE

        return rsp
