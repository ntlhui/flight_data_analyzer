from ubuntu:16.04
RUN apt-get update && apt-get install -y git vim htop gdb python3 python3-pip \
	tmux software-properties-common unzip wget
RUN pip3 install --upgrade pip
RUN pip3 install pymavlink numpy scipy ipython pyshp jupyter hvplot seaborn calmap folium opencv-python matplotlib selenium

WORKDIR /tmp
RUN apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1 -y
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

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