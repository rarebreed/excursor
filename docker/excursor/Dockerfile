FROM python:3.11.3

ARG userid=1750
ARG groupid=1752

RUN apt update && apt upgrade -y && \
    addgroup --system --gid $groupid app && \
    adduser --system --home /home/app --ingroup app --shell /bin/bash --uid $userid app
WORKDIR /home/app
USER app
ENV PATH=$PATH:/home/app/.local/bin

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install -U pip && \
    pip install pipx && \
    pipx ensurepath && \
    pipx install poetry && \
    mkdir code 

WORKDIR code
COPY . .

RUN . /home/app/venv/bin/activate && \
    poetry install --all-extras --with dev

CMD ["poetry", "-V"]