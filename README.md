# yagna-docker
Run yagna provider for developing purposes. 
Works on Linux and Windows with WSL2 backend. 
On OSX only parts without runtime-vm works sadly (blame Apple).

## Motivation

This repository is a collection of docker-compose files for running yagna provider in development mode.

Running providers without docker although it is good for production, it is not easy for testing.
If you want to run mulitple yagna provider instances you will run into issues like port conflicts, data folder issues etc.

The best solution for development is to run yagna in separated docker containers.

There are two schools, one to use one configuration for all providers (scaling in docker compose), but in my opinion it is a bit too limited.
The second is to use separate configuration for each provider. This is the way I choose in provider directory.
That's why created python script to generate docker-compose file, which might sound like overkill, but in my opinion is
not so complicated yet give more flexibility. You can of course edit docker-compose file manually, but it is prone to errors, like missing a port or other mapping.

I choose to use python as base image for generating docker file, because I found it very universal and powerful. If you want 
to use lighter image you are free to modify Dockerfile according to your needs.

## instructions

instructions for running own development providers 
[here](provider/README.md)