FROM ubuntu:latest

RUN apt-get update && \
    apt-get -y install git python python-pip

RUN git clone http://craig.koroscil@stash.secure.root9b.com/scm/dev/scadasim-plc.git

WORKDIR /scadasim-plc

RUN make

EXPOSE 502

ENTRYPOINT python scadasim_plc/plc.py
