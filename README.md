## Scrapp-e Core

ROS package for Scrapp-e
<!-- add a more in depth description of scrapp-e as a whole later -->


<!-- ros-examples contains the repo for official ros package examples -->


## Dev environment setup
Note: these steps require docker to be installed on your machine.
### Building image
After cloning the repository, navigate to the /docker folder, then run the docker build command:

```
docker build -t scrapp-e-dev:latest -f ./dev-environment.Dockerfile .
```

this will create the dev environment image in docker with the name/version tag 'scrapp-e-dev:latest'

### Creating container

Run the docker start command, specifying the dev environment image:

```
docker run -it scrapp-e-dev:latest
```
This command creates and subsequently starts a docker container using the image, providing a interactive shell connected to the machine. Use the `exit ` command to exit the shell/turn the container off.
<!-- might change later to just be the create command, works for now though -->


### Running container
List all containers, find the one that uses the Scrapp-e dev image.
```
$ docker ps --all
```

Start the container using its container ID (-i flag attaches a command line interface to your terminal session to interact with the controller)

```
$ docker start -i [CONTAINERID]
```

## Deployment for Scrapp-e/Raspberry Pi based testbed
<!-- put instructions for docker compose -->