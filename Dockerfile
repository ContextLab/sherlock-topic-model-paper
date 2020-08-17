FROM debian:latest

# Install necessary linux packages from apt-get
RUN apt-get update --fix-missing && apt-get install -y eatmydata

RUN eatmydata apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git \
    libfreetype6-dev \
    swig \
    mpich \
    pkg-config \
    gcc \
    wget \
    curl \
    vim \
    nano

# Install anaconda
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

# Setup anaconda path
ENV PATH /opt/conda/bin:$PATH

# Enable UTF-8 locale
ENV LANG C.UTF-8

# Install gcc to make it work with brainiak
RUN ["/bin/bash", "-c", "conda install -y gcc"]

# update setuptools
RUN conda update setuptools

# Install packages
RUN pip install \
    numpy==1.17.0 \
    pandas==0.25.0 \
    matplotlib==3.1.0 \
    seaborn==0.9.0 \
    hypertools==0.6.2 \
    scikit-learn==0.19.1 \
    git+git://github.com/nilearn/nilearn.git@c0d14098c6b56381e4b527ca21986f86955cbf4f \
    git+https://github.com/brainiak/brainiak.git@v0.7.1 \
    git+git://github.com/ContextLab/quail.git@71dd53c792dd915dc84879d8237e3582dd68b7a4#egg=quail \
    fastdtw==0.3.2 \
    wordcloud==1.5.0 \
    pycircstat==0.0.2 \
    scipy==1.2.1 \ 
    xlrd==1.1.0 

# Define a bash function to simplify notebook launch command
RUN echo 'jupyter() { if [[ $@ == "notebook" ]]; then command jupyter notebook /mnt/code/notebooks --port=9999 --no-browser --ip=0.0.0.0 --allow-root; else command jupyter "$@"; fi; }' >> /root/.bashrc

# Set launch command to install helpers package the first time container is run
CMD ["/bin/bash", "-c", "source /root/.bashrc && [ -z $HELPERS_INSTALLED ] && { echo \"installing sherlock-helpers package\" && python -W ignore -m  pip install -qe code/sherlock_helpers && echo 'HELPERS_INSTALLED=1' >> /root/.bashrc; }; /bin/bash"]

# Set default working directory to repo mountpoint
WORKDIR /mnt

# Finally, expose a port from within the docker so we can use it to run jupyter notebooks
EXPOSE 9999