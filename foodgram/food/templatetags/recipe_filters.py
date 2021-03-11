from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def get_from_dict(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_value_from_list(list, index):
    return list[index]


@register.filter
def parse_tags(get):
    return get.getlist("tag")


@register.filter
def set_tag_qs(request, tag):
    new_req = request.GET.copy()
    tags = new_req.getlist("tag")
    if tag.eng_name in tags:
        tags.remove(tag.eng_name)
    else:
        tags.append(tag.eng_name)
    new_req.setlist("tag", tags)
    return new_req.urlencode()
