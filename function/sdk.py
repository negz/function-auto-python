import logging
import os

import grpc
import structlog
from grpc_reflection.v1alpha import reflection

import function.proto.v1beta1.run_function_pb2 as fnv1beta1
import function.proto.v1beta1.run_function_pb2_grpc as grpcv1beta1

SERVICE_NAMES = (
    reflection.SERVICE_NAME,
    fnv1beta1.DESCRIPTOR.services_by_name["FunctionRunnerService"].full_name,
)


def load_credentials(tls_certs_dir: str) -> grpc.ServerCredentials:
    if tls_certs_dir is None:
        return None

    with open(os.path.join(tls_certs_dir, "tls.crt"), "rb") as f:
        crt = f.read()

    with open(os.path.join(tls_certs_dir, "tls.key"), "rb") as f:
        key = f.read()

    with open(os.path.join(tls_certs_dir, "ca.crt"), "rb") as f:
        ca = f.read()

    return grpc.ssl_server_credentials(
        private_key_certificate_chain_pairs=((key, crt)),
        root_certificates=ca,
        require_client_auth=True,
    )


def configure_logging(*, debug: bool) -> None:
    processors = [
        structlog.stdlib.add_log_level,
    ]

    if debug:
        structlog.configure(
            processors=[
                *processors,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(colors=False),
            ]
        )
        return

    # Attempt to match function-sdk-go's production logger.
    structlog.configure(
        processors=[
            *processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.TimeStamper(key="ts"),
            structlog.processors.EventRenamer(to="msg"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


async def serve(
    function: grpcv1beta1.FunctionRunnerService, address: str, *, creds: grpc.ServerCredentials, insecure: bool
) -> None:
    server = grpc.aio.server()

    grpcv1beta1.add_FunctionRunnerServiceServicer_to_server(function, server)
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    if creds is not None:
        server.add_secure_port(address, creds)

    # TODO(negz): Does this override add_secure_port?
    if insecure:
        server.add_insecure_port(address)

    await server.start()
    await server.wait_for_termination()
