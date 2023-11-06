import asyncio

import click

from function import fn, sdk


@click.command()
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Emit debug logs.",
)
@click.option(
    "--address",
    default="0.0.0.0:9443",
    show_default=True,
    help="Address at which to listen for gRPC connections",
)
@click.option(
    "--tls-certs-dir",
    help="Serve using mTLS certificates.",
    envvar="TLS_SERVER_CERTS_DIR",
)
@click.option(
    "--insecure",
    is_flag=True,
    help="Run without mTLS credentials. "
    "If you supply this flag --tls-certs-dir will be ignored.",
)
def cli(debug: bool, address: str, tls_certs_dir: str, insecure: bool) -> None:  # noqa:FBT001  # We only expect callers via the CLI.
    """A Crossplane Composition Function."""
    sdk.configure_logging(debug=debug)
    asyncio.run(
        sdk.serve(
            fn.FunctionRunner(),
            address,
            creds=sdk.load_credentials(tls_certs_dir),
            insecure=insecure,
        )
    )


if __name__ == "__main__":
    cli()