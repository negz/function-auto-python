# function-auto-python

[function-auto-ready], but Python.

I'm using this experimental composition function to prototype how functions
could be built using Python.

Development uses [Hatch][hatch]. Some useful commands:

```shell
# Lint the code
hatch run lint:check

# Run tests
hatch run unit:test

# Run locally (e.g. for crossplane beta render)
hatch run python function/main.py --insecure --debug

# Build the function runtime image
docker build .
```

[function-auto-ready]: https://github.com/crossplane-contrib/function-auto-ready
[hatch]: https://github.com/pypa/hatch