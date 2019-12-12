# How is experience transformed into memory?

This repository contains data and code used to produce the paper "[_How is experience transformed into memory_](https://www.biorxiv.org/content/early/2018/09/06/409987)" by Andrew C. Heusser, Paxton C. Fitzpatrick, and Jeremy R. Manning. The repository is organized as follows:

```
root
└── code : all code used in the paper
    ├── notebooks : jupyter notebooks for paper analyses
    └── scripts : python scripts used to perform various analyses on a cluster
        ├── embedding : scripts used to optimize the UMAP embedding seed for the trajectory figure
        └── searchlights : scripts used to perform the brain searchlight analyses
└── data : all data used in the paper
    ├── raw : raw data before processing
    └── processed : all processed data
└── paper : all files to generate paper
    └── figs : pdf copies of each figure
```

We also include a Dockerfile to reproduce our computational environment. Instruction for use are below (copied and modified from [MIND](https://github.com/Summer-MIND/mind-tools) repo):

## One time setup
1. Install Docker on your computer using the appropriate guide below:
    - [OSX](https://docs.docker.com/docker-for-mac/install/#download-docker-for-mac)
    - [Windows](https://docs.docker.com/docker-for-windows/install/)
    - [Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
    - [Debian](https://docs.docker.com/engine/installation/linux/docker-ce/debian/)
2. Launch Docker and adjust the preferences to allocate sufficient resources (e.g. > 4GB RAM)
3. Build the docker image by opening a terminal in this repo folder and enter `docker build -t sherlock .`  
4. Use the image to create a new container for the workshop
    - The command below will create a new container that will map your computer's `Desktop` to `/mnt` within the container, so that location is shared between your host OS and the container. Feel free to change `Desktop` to whatever folder you prefer to share instead, but make sure to provide the full path. The command will also share port `9999` with your host computer so any jupyter notebooks launched from *within* the container will be accessible at `localhost:9999` in your web browser
    - `docker run -it -p 9999:9999 --name Sherlock -v ~/Desktop:/mnt sherlock `
    - You should now see the `root@` prefix in your terminal, if so you've successfully created a container and are running a shell from *inside*!
5. To launch any of the notebooks: `jupyter lab --port=9999 --no-browser --ip=0.0.0.0 --allow-root`

## Using the container after setup
1. You can always fire up the container by typing the following into a terminal
    - `docker start Sherlock && docker attach Sherlock`
    - When you see the `root@` prefix, letting you know you're inside the container
2. Close a running container with `ctrl + d` from the same terminal you used to launch the container, or `docker stop Sherlock` from any other terminal
