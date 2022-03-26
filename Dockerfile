FROM python:3

WORKDIR /

RUN git clone https://github.com/Tw1sm/spraycharles
WORKDIR spraycharles
RUN pip3 install -r requirements.txt
RUN chmod +x /spraycharles/spraycharles.py

ENTRYPOINT ["./spraycharles.py"]
