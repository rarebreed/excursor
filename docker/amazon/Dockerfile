FROM amazonlinux:latest

RUN mkdir app && \
    dnf install -y python pip
WORKDIR /app
COPY . .

CMD ["bash", "-V"]