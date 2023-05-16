from neighbourhood.mapit import (BadRequestException, ForbiddenException,
                                 InternalServerErrorException, MapIt,
                                 NotFoundException)


def get_postcode_centroid(postcode):
    if postcode is None:
        return {"error": "Postcode is blank"}

    mapit = MapIt()
    try:
        lat_lon = mapit.postcode_point_to_centroid(postcode)

        return lat_lon
    except (
        NotFoundException,
        BadRequestException,
        InternalServerErrorException,
        ForbiddenException,
    ) as error:
        return {"error": error}


def find_where(list_of_dicts, properties):
    """Looks through the list_of_dicts and returns the first dict that matches all of the key-value pairs listed in properties. If no match is found, or if list_of_dicts is empty, None is returned."""
    for d in list_of_dicts:
        if all(d[key] == value for key, value in properties.items()):
            return d
    return None
