FROM python:slim

WORKDIR /

RUN apt-get update && apt-get install git -y
RUN pip3 install pipx
RUN pipx ensurepath
RUN pipx install git+https://github.com/Tw1sm/spraycharles.git

ENTRYPOINT ["/root/.local/bin/spraycharles"]
