FROM thierrytct/klee-semu-relmut:llvm-3.4.2

# Create docker user
RUN apt-get update && \
    apt-get install --no-install-recommends -y sudo && \
    useradd -ms /bin/bash docker && \
    echo 'docker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    adduser docker sudo && \
    apt-get clean && \
    mkdir -p /home/docker && \
    sudo chown -R docker /home/docker && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
USER docker

# reclaim ownership of /usr/local/bin
RUN sudo chown -R docker /usr/local/bin

# install basic packages
RUN sudo apt-get update && \
    sudo apt-get install  --no-install-recommends -y \
                          build-essential \
                          gcc \
                          patch \
                          curl \
                          libcap-dev \
                          git \
                          cmake \
                          vim \
                          jq \
                          tar \
                          psmisc \
                          moreutils \
                          wget \
                          zip \
                          unzip \
                          python3-setuptools \
                          python \
                          software-properties-common \
                          gcovr \
                          libncurses5-dev && \
    sudo apt-get autoremove -y && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Fix /bin/sh to point to /bin/bash
RUN sudo rm /bin/sh && \
    sudo ln -s /bin/bash /bin/sh

# install Bear
RUN cd /tmp \
 && wget https://github.com/rizsotto/Bear/archive/2.3.13.tar.gz \
 && tar -xf 2.3.13.tar.gz \
 && cd Bear-2.3.13 \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make \
 && sudo make install \
 && rm -rf /tmp/*

# Create the experiment directory and set it as the work dir
RUN sudo mkdir -p /experiment && sudo chown -R docker /experiment
WORKDIR /experiment

# add generic preprocessing script
COPY base/preprocess /experiment/preprocess

COPY compile.sh /experiment/compile.sh
RUN sudo chown -R docker /experiment && \
    sudo chmod +x compile.sh
