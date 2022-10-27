# Back-End Server
The SUFST back-end server. This server acts as a **Web-Socket** server and has 2 main purposes.

- The intermediate-server connects to it to distribute all the data from the Xbee module. 
- The front-end clients connect to it to perform all authentication operations, CRUD actions and retrieve live sensor data.

## Running
To run the server you first need to have Docker installed on your machine. The recommended way to do this in Windows and macOS is with the Docker Desktop application. Installing this will also install the `docker` command on your machine. 

If you use macOS, you can also install Docker with Homebrew. 

You also need to have `git` installed on your machine. Instructions for how to do this on all major Operating Systems are provided in the SUFST Documentation website. 

Now follow the steps below:  

#### 1. Clone the Repository
Open a terminal window, navigate to a folder of your choice and run the following command to clone the repository from GitHub. 

```
git clone https://github.com/sufst/back-end.git
```

When this is done, change directory into the cloned folder using `cd back-end`. 

#### 2. Launch Docker 
From within the `back-end` folder, simply run the `run_docker.sh` script. This will build a Docker image and launch a container with that image. For this, run: 

```
bash run_docker.sh
```

You can also run the script using `./run_docker.sh` however make sure to first give it the appropriate permissions using `chmod`. 
