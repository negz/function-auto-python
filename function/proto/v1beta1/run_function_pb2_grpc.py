# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from function.proto.v1beta1 import run_function_pb2 as function_dot_proto_dot_v1beta1_dot_run__function__pb2


class FunctionRunnerServiceStub(object):
    """A FunctionRunnerService is a Composition Function.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RunFunction = channel.unary_unary(
                '/apiextensions.fn.proto.v1beta1.FunctionRunnerService/RunFunction',
                request_serializer=function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionRequest.SerializeToString,
                response_deserializer=function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionResponse.FromString,
                )


class FunctionRunnerServiceServicer(object):
    """A FunctionRunnerService is a Composition Function.
    """

    def RunFunction(self, request, context):
        """RunFunction runs the Composition Function.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FunctionRunnerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RunFunction': grpc.unary_unary_rpc_method_handler(
                    servicer.RunFunction,
                    request_deserializer=function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionRequest.FromString,
                    response_serializer=function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'apiextensions.fn.proto.v1beta1.FunctionRunnerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FunctionRunnerService(object):
    """A FunctionRunnerService is a Composition Function.
    """

    @staticmethod
    def RunFunction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/apiextensions.fn.proto.v1beta1.FunctionRunnerService/RunFunction',
            function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionRequest.SerializeToString,
            function_dot_proto_dot_v1beta1_dot_run__function__pb2.RunFunctionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)