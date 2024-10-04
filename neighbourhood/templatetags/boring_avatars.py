import math
import uuid

from django import template
from django.template import Context, Template

register = template.Library()


@register.simple_tag
def boring_avatar(**kwargs):
    # A Python/Django port of Josep Martins and Hayk An’s
    # MIT licensed "Boring Avatars" JavaScript library
    # https://github.com/boringdesigners/boring-avatars

    context = {}

    context["viewport_size"] = 36
    context["name"] = kwargs.get("name")
    context["colors"] = kwargs.get(
        "colors", ["#fcbf49", "#eae2b7", "#198754", "#d62828", "#ccc7ab"]
    )
    context["title"] = kwargs.get("title", False)
    context["square"] = kwargs.get("square", True)

    context["other_props"] = {
        k: v
        for k, v in kwargs.items()
        if k not in ["name", "colors", "title", "square"]
    }

    context["viewport_half"] = context["viewport_size"] / 2
    context["viewport_double"] = context["viewport_size"] * 2
    context["mask_id"] = uuid.uuid4()

    num_from_name = hash_code(context["name"])
    pre_translate_x = get_unit(num_from_name, 10, 1)
    pre_translate_y = get_unit(num_from_name, 10, 2)

    context["is_circle"] = get_boolean(num_from_name, 1)
    context["wrapper_color"] = get_offset_item(num_from_name, context["colors"])
    context["face_color"] = get_contrast(context["wrapper_color"])
    context["background_color"] = get_offset_item(num_from_name + 13, context["colors"])
    context["wrapper_translate_x"] = (
        pre_translate_x + context["viewport_size"] / 9
        if pre_translate_x < 5
        else pre_translate_x
    )
    context["wrapper_translate_y"] = (
        pre_translate_y + context["viewport_size"] / 9
        if pre_translate_y < 5
        else pre_translate_y
    )
    context["wrapper_rotate"] = get_unit(num_from_name, 360)
    context["wrapper_scale"] = (
        1 + get_unit(num_from_name, context["viewport_size"] / 12) / 10
    )
    context["wrapper_radius"] = (
        context["viewport_size"]
        if context["is_circle"]
        else (context["viewport_size"] / 6)
    )
    context["is_mouth_open"] = get_boolean(num_from_name, 2)
    context["eye_spread"] = get_unit(num_from_name, 5)
    context["mouth_spread"] = get_unit(num_from_name, 3) + 19
    context["face_rotate"] = get_unit(num_from_name, 10, 3)
    context["face_translate_x"] = (
        context["wrapper_translate_x"] / 2
        if context["wrapper_translate_x"] > context["viewport_size"] / 6
        else get_unit(num_from_name, 8, 1)
    )
    context["face_translate_y"] = (
        context["wrapper_translate_y"] / 2
        if context["wrapper_translate_y"] > context["viewport_size"] / 6
        else get_unit(num_from_name, 7, 2)
    )
    context["left_eye_x"] = 14 - context["eye_spread"]
    context["right_eye_x"] = 20 + context["eye_spread"]

    template = Template(
        """
    <svg
      viewBox="0 0 {{viewport_size}} {{viewport_size}}"
      fill="none"
      role="img"
      xmlns="http://www.w3.org/2000/svg"
    {% for key, value in other_props.items %}
      {{key}}="{{value}}"
    {% endfor %}
    >
      {% if title %}
        <title>{{name}}</title>
      {% endif %}
        <mask id="{{mask_id}}" maskUnits="userSpaceOnUse" x="0" y="0" width="{{viewport_size}}" height="{{viewport_size}}">
            <rect width="{{viewport_size}}" height="{{viewport_size}}" {% if not square %}rx="{{viewport_double}}"{% endif %} fill="#FFFFFF" />
        </mask>
        <g mask="url(#{{mask_id}})">
            <rect width="{{viewport_size}}" height="{{viewport_size}}" fill="{{background_color}}" />
            <rect
              x="0"
              y="0"
              width="{{viewport_size}}"
              height="{{viewport_size}}"
              transform="translate({{wrapper_translate_x}} {{wrapper_translate_y}}) rotate({{wrapper_rotate}} {{viewport_half}} {{viewport_half}}) scale({{wrapper_scale}})"
              fill="{{wrapper_color}}"
              rx="{{wrapper_radius}}"
            />
            <g transform="translate({{face_translate_x}} {{face_translate_y}}) rotate({{face_rotate}} {{viewport_half}} {{viewport_half}})">
              {% if is_mouth_open %}
                <path
                  d="M15 {{mouth_spread}}c2 1 4 1 6 0"
                  stroke="{{face_color}}"
                  fill="none"
                  strokeLinecap="round"
                />
              {% else %}
                <path
                  d="M13,{{mouth_spread}} a1,0.75 0 0,0 10,0"
                  fill="{{face_color}}"
                />
              {% endif %}
                <rect
                  x="{{left_eye_x}}"
                  y="14"
                  width="1.5"
                  height="2"
                  rx="1"
                  stroke="none"
                  fill="{{face_color}}"
                />
                <rect
                  x="{{right_eye_x}}"
                  y="14"
                  width="1.5"
                  height="2"
                  rx="1"
                  stroke="none"
                  fill="{{face_color}}"
                />
            </g>
        </g>
    </svg>
    """
    )

    return template.render(Context(context))


def get_boolean(number, ntn):
    return get_digit(number, ntn) % 2 == 0


def get_contrast(hexcolor):
    if hexcolor.startswith("#"):
        hexcolor = hexcolor[1:]

    r = int(hexcolor[0:2], 16)
    g = int(hexcolor[2:4], 16)
    b = int(hexcolor[4:6], 16)

    yiq = (r * 299 + g * 587 + b * 114) / 1000

    return "#000000" if yiq >= 128 else "#FFFFFF"


def get_digit(number, ntn):
    return math.floor((number / (10**ntn)) % 10)


def get_offset_item(offset, items):
    return items[offset % len(items)]


def get_unit(number, range_, index=None):
    value = number % range_

    if index is not None and get_digit(number, index) % 2 == 0:
        return -value
    else:
        return value


def hash_code(name):
    """Create a positive integer hash of the given string"""
    hash_value = 0

    for character in name:
        hash_value = (hash_value << 5) - hash_value + ord(character)
        # Convert to 32-bit integer
        hash_value = hash_value & 0xFFFFFFFF

    # Handle negative values (like JavaScript original did)
    if hash_value >= 0x80000000:
        hash_value -= 0x100000000

    return abs(hash_value)
