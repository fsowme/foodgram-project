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
def get_tag_params(request, tag):
    request_ = request.GET.copy()
    tags_names = request_.getlist("disable")
    if tag.eng_name in tags_names:
        tags_names.remove(tag.eng_name)
    else:
        tags_names.append(tag.eng_name)
    request_.setlist("disable", tags_names)
    return request_.urlencode()
