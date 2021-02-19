# Geometric models reveal behavioural and neural signatures of transforming naturalistic experiences into episodic memories

<p align="center"
  <a href="https://www.nature.com/articles/s41562-021-01051-6">
    <img src="https://img.shields.io/badge/paper-Nature%20Human%20Behaviour-blue.svg" alt="Paper (Nature Human Behaviour)">
  </a>
  <a href="https://rdcu.be/cfsYs">
    <img src="https://img.shields.io/badge/paper-PDF-blue.svg" alt="Paper (Direct PDF link)">
  </a>
  <a href="https://socialsciences.nature.com/posts/how-is-experience-transformed-into-memory">
    <img src="https://img.shields.io/badge/Behind%20the%20Paper-blog%20post-blue.svg" alt="Behind the Paper (blog post)">
  </a>
</p>

This repository contains data and code used to produce the paper "[_Geometric models reveal behavioural and neural signatures of transforming naturalistic experiences into episodic memories_](https://rdcu.be/cfsYs)" by Andrew C. Heusser, Paxton C. Fitzpatrick, and Jeremy R. Manning.

The repository is organized as follows:

```yaml
root
├── code : all analysis code used in the paper
│   ├── notebooks : Jupyter notebooks for paper analyses
│   ├── scripts : Python scripts for running analyses on a HPC cluster (Moab/TORQUE)
│   │   ├── embedding : scripts for optimizing the UMAP embedding for the trajectory figure
│   │   └── searchlights : scripts for performing the brain searchlight analyses
│   └── sherlock_helpers : Python package with support code for analyses
├── data : all data analyzed in the paper
│   └── raw : raw video annotations and recall transcripts
│   └── processed : all processed data
└── paper : all files to generate paper
    └── figs : pdf copies of all figures
```

We also include a `Dockerfile` to reproduce our computational environment. Instruction for use are below (copied and modified from the [MIND](https://github.com/Summer-MIND/mind-tools) repo):

## One time setup
1. Install Docker on your computer using the appropriate guide below:
    - [OSX](https://docs.docker.com/docker-for-mac/install/#download-docker-for-mac)
    - [Windows](https://docs.docker.com/docker-for-windows/install/)
    - [Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
    - [Debian](https://docs.docker.com/engine/installation/linux/docker-ce/debian/)
2. Launch Docker and adjust the preferences to allocate sufficient resources (e.g. >= 4GB RAM)
3. To build the Docker image, open a terminal window, navigate to your local copy of the repo, and run `docker build -t sherlock .`  
4. Use the image to run a container with the repo mounted as a volume so the code and data are accessible.
    - The command below will create a new container that maps the repository on your computer to the `/mnt` directory within the container, so that location is shared between your host OS and the container. Be sure to replace `LOCAL/REPO/PATH` with the path to the cloned repository on your own computer (you can get this by navigating to the repository in the terminal and typing `pwd`).  The below command will also share port `9999` with your host computer, so any Jupyter notebooks launched from *within* the container will be accessible at `localhost:9999` in your web browser
    - `docker run -it -p 9999:9999 --name Sherlock -v /LOCAL/REPO/PATH:/mnt sherlock `
    - You should now see the `root@` prefix in your terminal. If you do, then you've successfully created a container and are running a shell from *inside*!
5. To launch any of the notebooks, simply enter `jupyter notebook` and copy/paste the link generated into your browser.

## Using the container after setup
1. You can always fire up the container by typing the following into the terminal
    - `docker start Sherlock && docker attach Sherlock`
    - When you see the `root@` prefix, letting you know you're inside the container
2. If you launch the notebooks, you'll notice your shell is occupied by the output log from the `jupyter` server.  To stop the notebook server, press `ctrl + c`, and then `y` when prompted.
3. To close the running container, press `ctrl + d`  or type `exit` from the same terminal window you used to launch the container.
4. You can also open a second bash shell inside the container simultaneously by running `docker exec -it Sherlock bash` from the terminal *outside* the container.  Note that when you enter the container this way (rather than by using `docker attach Sherlock`), the container isn't automatically stopped when you exit it.  To stop the container after exiting, enter `docker stop Sherlock`.
