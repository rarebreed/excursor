FROM debian:bookworm

# RUN addgroup --system --gid $groupid app && \
#     adduser --system --home /home/app --ingroup app --shell /bin/bash --uid $userid app

RUN mkdir app && \
    apt install python curl wget
WORKDIR /app
COPY . .

CMD ["bash", "-V"]