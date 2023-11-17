"""A composition function SDK."""

import asyncio
import dataclasses
import datetime
import logging
import os

import grpc
import structlog
from google.protobuf import struct_pb2 as structpb
from grpc_reflection.v1alpha import reflection

import function.proto.v1beta1.run_function_pb2 as fnv1beta1
import function.proto.v1beta1.run_function_pb2_grpc as grpcv1beta1

SERVICE_NAMES = (
    reflection.SERVICE_NAME,
    fnv1beta1.DESCRIPTOR.services_by_name["FunctionRunnerService"].full_name,
)


def load_credentials(tls_certs_dir: str) -> grpc.ServerCredentials:
    """Load TLS credentials for a composition function gRPC server.

    Args:
        tls_certs_dir: A directory containing tls.crt, tls.key, and ca.crt.

    Returns:
        gRPC mTLS server credentials.

    tls.crt and tls.key must be the function's PEM-encoded certificate and
    private key. ca.cert must be a PEM-encoded CA certificate used to
    authenticate callers (i.e. Crossplane).
    """
    if tls_certs_dir is None:
        return None

    with open(os.path.join(tls_certs_dir, "tls.crt"), "rb") as f:
        crt = f.read()

    with open(os.path.join(tls_certs_dir, "tls.key"), "rb") as f:
        key = f.read()

    with open(os.path.join(tls_certs_dir, "ca.crt"), "rb") as f:
        ca = f.read()

    return grpc.ssl_server_credentials(
        private_key_certificate_chain_pairs=[(key, crt)],
        root_certificates=ca,
        require_client_auth=True,
    )


def configure_logging(*, debug: bool) -> None:
    """Configure logging.

    Args:
        debug: Whether to enable debug logging.

    Must be called before calling get_logger. When debug logging is enabled logs
    will be printed in a human readable fashion. When not enabled, logs will be
    printed as JSON lines.
    """
    processors = [
        structlog.stdlib.add_log_level,
    ]

    if debug:
        structlog.configure(
            processors=[
                *processors,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
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


def get_logger() -> structlog.stdlib.BoundLogger:
    """Get a logger.

    You must call configure_logging before calling get_logger.
    """
    return structlog.stdlib.get_logger()


def serve(
    function: grpcv1beta1.FunctionRunnerService,
    address: str,
    *,
    creds: grpc.ServerCredentials,
    insecure: bool,
) -> None:
    """Start a gRPC server and serve requests asychronously.

    Args:
        function: The function (class) to use to serve requests.
        address: The address at which to listen for requests.
        creds: The credentials used to authenticate requests.
        insecure: Serve insecurely, without credentials or encryption.

    Raises:
        ValueError if creds is None and insecure is False.

    If insecure is true requests will be served insecurely, even if credentials
    are supplied.
    """
    server = grpc.aio.server()

    grpcv1beta1.add_FunctionRunnerServiceServicer_to_server(function, server)
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    if creds is None and insecure is False:
        msg = (
            "no credentials were provided - did you provide credentials or use "
            "the insecure flag?"
        )
        raise ValueError(msg)

    if creds is not None:
        server.add_secure_port(address, creds)

    # TODO(negz): Does this override add_secure_port?
    if insecure:
        server.add_insecure_port(address)

    async def start():
        await server.start()
        await server.wait_for_termination()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    finally:
        loop.run_until_complete(server.stop(grace=5))
        loop.close()


@dataclasses.dataclass
class Condition:
    """A status condition."""

    """Type of the condition - e.g. Ready."""
    typ: str

    """Status of the condition - True, False, or Unknown."""
    status: str

    """Reason for the condition status - typically CamelCase."""
    reason: str | None = None

    """Optional message."""
    message: str | None = None

    """The last time the status transitioned to this status."""
    last_transition_time: datetime.time | None = None


def get_condition(resource: structpb.Struct, typ: str) -> Condition:
    """Get the supplied status condition of the supplied resource.

    Args:
        resource: A Crossplane resource.
        typ: The type of status condition to get (e.g. Ready).

    Returns:
        The requested status condition.

    A status condition is always returned. If the status condition isn't present
    in the supplied resource, a condition with status "Unknown" is returned.
    """
    unknown = Condition(typ=typ, status="Unknown")

    if "status" not in resource:
        return unknown

    if "conditions" not in resource["status"]:
        return unknown

    for c in resource["status"]["conditions"]:
        if c["type"] != typ:
            continue

        condition = Condition(
            typ=c["type"],
            status=c["status"],
        )
        if "message" in c:
            condition.message = c["message"]
        if "reason" in c:
            condition.reason = c["reason"]
        if "lastTransitionTime" in c:
            condition.last_transition_time = datetime.datetime.fromisoformat(
                c["lastTransitionTime"]
            )

        return condition

    return unknown


def response_from(req: fnv1beta1.RunFunctionRequest) -> fnv1beta1.RunFunctionResponse:
    """Create a response to the supplied request."""
    return fnv1beta1.RunFunctionResponse(
        meta=fnv1beta1.ResponseMeta(tag=req.meta.tag),
        desired=req.desired,
        context=req.context,
    )
