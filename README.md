# function-auto-python

[function-auto-ready], but Python.

I'm using this experimental composition function to prototype how functions
could be built using Python. The eventual goal would be to refactor most of
this out into function-sdk-python and function-template-python.

TODO:

* Break the `function.sdk` package out into a PyPI package.

Development uses [Hatch][hatch]. I chose it from an [overwhelming ecosystem of
build tools][too-many-tools] because:

* It seems official and standards compliant, at least compared to e.g. Poetry.
* It can work for libraries (e.g. function-sdk-python), not just apps.
* It's used by httpx, fastapi, and a few other modern Python tools I surveyed.

Some useful commands:

```shell
# Generate gRPC stubs.
hatch run generate:protoc

# Run locally (e.g. for crossplane beta render)
hatch run python function/main.py --insecure --debug

# Build a Dockerfile
docker build .
```

[function-auto-ready]: https://github.com/crossplane-contrib/function-auto-ready
[hatch]: https://github.com/pypa/hatch
[too-many-tools]: https://chriswarrick.com/blog/2023/01/15/how-to-improve-python-packaging/