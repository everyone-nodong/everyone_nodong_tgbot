FROM python:3.13

RUN apt update
RUN apt install -y pipx
RUN pipx install poetry==2.0.0

ENV PATH="/root/.local/bin:$PATH"

COPY poetry.lock pyproject.toml /app/

WORKDIR /app/

RUN poetry install

COPY everyone_nodong_bot /app/everyone_nodong_bot/

ENTRYPOINT ["poetry", "run", "python", "-m", "everyone_nodong_bot.main"]