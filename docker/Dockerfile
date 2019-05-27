from ubuntu:16.04
RUN apt-get update && apt-get install -y git vim htop gdb python3 python3-pip \
	tmux software-properties-common unzip
RUN pip3 install --upgrade pip
RUN pip3 install pymavlink numpy scipy ipython pyshp jupyter

RUN add-apt-repository ppa:alessandro-strada/ppa
RUN apt-get update && apt-get install -y google-drive-ocamlfuse

RUN mkdir /root/.gdfuse/
WORKDIR /root/.gdfuse
COPY gdfuse_config.zip /root/.gdfuse
RUN unzip gdfuse_config.zip

RUN mkdir /root/gdrive
RUN echo 'google-drive-ocamlfuse /root/gdrive' >> /root/.bashrc

RUN mkdir /root/code

WORKDIR /root/code