import dataclasses
import unittest

from crossplane.function import logging, resource
from crossplane.function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from google.protobuf import duration_pb2 as durationpb
from google.protobuf import json_format
from google.protobuf import struct_pb2 as structpb

from function import fn


class TestFunctionRunner(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        logging.configure(level=logging.Level.DISABLED)

    async def test_run_function(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            reason: str
            req: fnv1beta1.RunFunctionRequest
            want: fnv1beta1.RunFunctionResponse

        cases = [
            TestCase(
                reason="An existing resource with unspecified readiness and a "
                "Ready: true status condition should be detected as ready.",
                req=fnv1beta1.RunFunctionRequest(
                    observed=fnv1beta1.State(
                        resources={
                            "ready-composed-resource": fnv1beta1.Resource(
                                resource=resource.dict_to_struct(
                                    {
                                        "apiVersion": "test.crossplane.io/v1",
                                        "kind": "Example",
                                        "status": {
                                            "conditions": [
                                                {"type": "Ready", "status": "True"},
                                            ],
                                        },
                                    }
                                ),
                            ),
                        }
                    ),
                    desired=fnv1beta1.State(
                        resources={
                            # This function doesn't care about the desired
                            # resource schema. In practice it would match
                            # observed (without status), but for this test it
                            # doesn't matter.
                            "ready-composed-resource": fnv1beta1.Resource(),
                        }
                    ),
                ),
                want=fnv1beta1.RunFunctionResponse(
                    meta=fnv1beta1.ResponseMeta(ttl=durationpb.Duration(seconds=60)),
                    desired=fnv1beta1.State(
                        resources={
                            # This function doesn't care about the desired
                            # resource schema. In practice it would match
                            # observed (without status), but for this test it
                            # doesn't matter.
                            "ready-composed-resource": fnv1beta1.Resource(
                                ready=fnv1beta1.READY_TRUE,
                            ),
                        }
                    ),
                    context=structpb.Struct(),
                ),
            ),
        ]

        runner = fn.FunctionRunner()

        for case in cases:
            got = await runner.RunFunction(case.req, None)
            self.assertEqual(
                json_format.MessageToJson(case.want),
                json_format.MessageToJson(got),
                "-want, +got",
            )


if __name__ == "__main__":
    unittest.main()
