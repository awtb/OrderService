import uvicorn
from typer import Option
from typer import Typer

app = Typer()


@app.command("start")
def start(
    host: str = Option("0.0.0.0"),
    port: int = Option(8000),
    reload: bool = Option(
        default=False,
    ),
) -> None:
    uvicorn.run(
        "order_service.app:build_app",
        reload=reload,
        port=port,
        host=host,
        factory=True,
    )


app()
