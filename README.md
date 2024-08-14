# Neighbourhood Warmth

An Alpha version of a tool to help neighbours signal their interest in exploring home energy efficiency improvements (“retrofit”) and leading them through those first steps, together.

The [original static prototype](https://github.com/mysociety/neighbourhood-warmth/tree/7be3169f2d647856ff882364d7413225192c60ee) was built as part of mySociety’s April 2022 prototyping week exploring how digital services might enable local climate action on energy through conditional commitment.

## Development install

You will need [Docker](https://docs.docker.com/desktop/) installed.

Clone the repository:

    git clone git@github.com:mysociety/neighbourhood-warmth.git
    cd neighbourhood-warmth

Then start the server:

    script/server

This will create a `.env` file (from `.env-example`) if one doesn’t already exist, and then run `script/server` again _inside_ a Docker container. You’ll be able to view the site at <https://localhost:8000>.

You may want to add your own `SECRET_KEY` and `MAPIT_API_KEY` to `.env`. You can get the latter from https://mapit.mysociety.org/account/signup/

If Python complains about missing libraries, chances are the Python requirements have changed since your Docker image was last built. You can rebuild it with, eg: `docker compose build web`.

You can run Django management commands inside the Docker container with `script/manage`, and you can create your first Django superuser with `script/createsuperuser` (which will use the `DJANGO_SUPERUSER_*` environment variables from `docker-compose.yml`).
