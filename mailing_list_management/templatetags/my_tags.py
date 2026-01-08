from django import template

register = template.Library()


@register.filter()
def media_filter_mailing_list_management(path):
    if path:
        return f"/media/{path}"
    return "#"
