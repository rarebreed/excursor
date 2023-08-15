FROM fedora:latest

# RUN addgroup --system --gid $groupid app && \
#     adduser --system --home /home/app --ingroup app --shell /bin/bash --uid $userid app

RUN dnf install which \
    mkdir app

CMD ["bash", "-V"]