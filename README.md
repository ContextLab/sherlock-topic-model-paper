# How is experience transformed into memory?

This repository contains data and code used to produce the paper "[_How is experience transformed into memory_](https://www.biorxiv.org/content/early/2018/09/06/409987)" by Andrew C. Heusser, Paxton C. Fitzpatrick, and Jeremy R. Manning. The repository is organized as follows:

```
root
├── code : all code used in the paper
│   ├── notebooks : jupyter notebooks for paper analyses
│   ├── scripts : python scripts used to perform various analyses on a cluster
│   │   ├── embedding : scripts used to optimize the UMAP embedding seed for the trajectory figure
│   │   └── searchlights : scripts used to perform the brain searchlight analyses
│   └── helpers : assorted helper scripts for downloading data
├── data : all data used in the paper
│   └── raw : raw data before processing
│   └── processed : all processed data
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
4. Use the image to create a new container for the workshop, with access to the data and code in the repo
    - The command below will create a new container that maps the repository on your computer to `/mnt` within the container, so that location is shared between your host OS and the container. Be sure to replace `path/to/repo` with the path to the cloned repository on your own computer, and make sure to provide the full path (You can get this by navigating to the repository in the terminal and typing `pwd`).  The below command will also share port `9999` with your host computer, so any jupyter notebooks launched from *within* the container will be accessible at `localhost:9999` in your web browser
    - `docker run -it -p 9999:9999 --name Sherlock -v /REPLACE/WITH/PATH/TO/REPO:/mnt sherlock `
    - You should now see the `root@` prefix in your terminal. If you do, then you've successfully created a container and are running a shell from *inside*!
5. To launch any of the notebooks, run `jupyter notebook --port=9999 --no-browser --ip=0.0.0.0 --allow-root` and copy/paste the link generated into your browser.

## Using the container after setup
1. You can always fire up the container by typing the following into a terminal
    - `docker start Sherlock && docker attach Sherlock`
    - When you see the `root@` prefix, letting you know you're inside the container
2. If you launch the notebooks, you'll notice your shell is occupied by the output log from the `jupyter` server.  To stop the notebook server, press `ctrl + c`, and then `y` when prompted.
3. To close the running container, press `ctrl + d`  or type `exit` from the same terminal you used to launch the container.
4. You can also open a second shell inside the container simultaneously by running `docker exec -it Sherlock bash` from the terminal *outside* the container.  Note that when you enter the container this way (rather than by using `docker attach Sherlock`), the container isn't automatically stopped when you exit it.  To stop the container after closing it, type `docker stop Sherlock`.
