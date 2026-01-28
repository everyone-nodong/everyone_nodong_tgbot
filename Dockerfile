FROM python:3.13

RUN pip install uv==0.9.27

ENV PATH="/root/.local/bin:$PATH"

COPY uv.lock pyproject.toml /app/

WORKDIR /app/

RUN uv sync

COPY everyone_nodong_bot /app/everyone_nodong_bot/

ENTRYPOINT ["uv", "run", "--no-sync"]
CMD ["python", "-m", "everyone_nodong_bot.main"]