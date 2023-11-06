import grpc
import structlog

from function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from function.proto.v1beta1 import run_function_pb2_grpc as grpcv1beta1


class FunctionRunner(grpcv1beta1.FunctionRunnerService):
    def __init__(self):
        self.log = structlog.get_logger()

    async def RunFunction(  # noqa:N802 # This is the interface gRPC generates.
        self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1beta1.RunFunctionResponse:
        self.log.info("Running function", tag=req.meta.tag)

        return fnv1beta1.RunFunctionResponse(
            desired=req.desired,
            results=[fnv1beta1.Result(severity=fnv1beta1.SEVERITY_NORMAL, message="Hello world!")],
        )
