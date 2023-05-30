FROM python:3.11.3

RUN apt update && apt upgrade -y

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ENV PATH=$PATH:/home/appuser/.local/bin

RUN echo $HOME && \
    pip install -U pip && \
    pip install pipx && \
    pipx ensurepath && \
    pipx install poetry && \
    mkdir code 

CMD ["poetry", "-V"]