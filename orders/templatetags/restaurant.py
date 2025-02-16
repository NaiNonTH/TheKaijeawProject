from django import template

register = template.Library()

def parse_fillings(values):
    values = [value.title for value in values]

    return " ".join(list(values))

register.filter("parse_fillings", parse_fillings)