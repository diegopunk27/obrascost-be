import os

import uvicorn

from app import create_app

app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "4000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
