FROM debian:latest

# RUN addgroup --system --gid $groupid app && \
#     adduser --system --home /home/app --ingroup app --shell /bin/bash --uid $userid app

RUN apt update && \
    apt upgrade -y && \
    mkdir /app &&\
    apt install -y wget curl python3 python3-pip git && \
    apt-get clean

WORKDIR /app
COPY . .

CMD ["bash", "-V"]