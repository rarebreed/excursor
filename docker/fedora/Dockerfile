FROM fedora:latest

# RUN addgroup --system --gid $groupid app && \
#     adduser --system --home /home/app --ingroup app --shell /bin/bash --uid $userid app

RUN mkdir app && \
    dnf install -y python curl wget pip
WORKDIR /app
COPY . .

CMD ["bash", "-V"]