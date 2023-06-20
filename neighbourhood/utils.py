from neighbourhood.mapit import (
    BadRequestException,
    ForbiddenException,
    InternalServerErrorException,
    MapIt,
    NotFoundException,
)


def get_mapit_data(call, *args):
    mapit = MapIt()
    try:
        method = getattr(mapit, call)
        data = method(*args)

        return data
    except (
        NotFoundException,
        BadRequestException,
        InternalServerErrorException,
        ForbiddenException,
    ) as error:
        return {"error": error}


def get_postcode_data(postcode):
    if postcode is None:
        return {"error": "Postcode is blank"}

    return get_mapit_data("postcode_point_to_data", postcode)


def get_postcode_centroid(postcode):
    if postcode is None:
        return {"error": "Postcode is blank"}

    return get_mapit_data("postcode_point_to_centroid", postcode)


def get_area_geometry(mapit_id):
    return get_mapit_data("area_id_to_geom", mapit_id)


def find_where(list_of_dicts, properties):
    """Looks through the list_of_dicts and returns the first dict that matches all of the key-value pairs listed in properties. If no match is found, or if list_of_dicts is empty, None is returned."""
    for d in list_of_dicts:
        if all(d[key] == value for key, value in properties.items()):
            return d
    return None
