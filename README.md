# Neighbourhood Warmth

## Development install

You will need [Docker](https://docs.docker.com/desktop/) installed.

Clone the repository:

    git clone git@github.com:mysociety/neighbourhood-warmth.git
    cd neighbourhood-warmth

Then start the container:

    script/server

This will create a `.env` file (from `.env-example`) if one doesn’t already exist, and then run `script/server` again _inside_ a Docker container.

If Python complains about missing libraries, chances are the Python requirements have changed since your Docker image was last built. You can rebuild it with, eg: `docker-compose build web`.
