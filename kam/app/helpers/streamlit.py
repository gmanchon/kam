
import streamlit as st

import re


MODEL_CLASS_ID_SEP = "___"

loaded_models = {}


def __build_model_string_id(model_klass, model_id):

    return f"{model_klass}{MODEL_CLASS_ID_SEP}{model_id}"


def __build_text_from_model(model_desc, model_id):

    model_text = f"{model_desc} ({model_id})"

    return model_text


def __retrieve_id_from_model_text(model_text):

    matches = re.compile(r"\([^\(]*\)$").search(model_text)

    # remove parenthesis
    model_id = matches[0][1:-1]

    return model_id


def model_to_text(model, model_desc):
    """
    returns reversible unique model textual representation
    """

    # build model string id
    model_string_id = __build_model_string_id(model.__class__, model.id)

    # store model
    loaded_models[model_string_id] = model

    # build textual representation
    model_text = __build_text_from_model(model_desc, model.id)

    return model_text


def text_to_model(model_text, models):
    """
    retrieve model attributes from textual representation
    """

    # retrieve model id from textual representation
    model_id = __retrieve_id_from_model_text(model_text)

    # build model string id
    model_string_id = __build_model_string_id(models[0].__class__, model_id)

    # retrieve model
    return loaded_models[model_string_id]


def st_radio(label, models, model_formatter, context=st, key=None):
    """
    streamlit radio helper allowing to select a model from a list of models
    """

    # format model choices
    model_choices = [model_to_text(m, model_formatter(m)) for m in models]

    # create radio button
    selected_assessment = context.radio(
        label,
        model_choices,
        key=f"st_radio_{label}" if key is None else key)

    # convert selected model
    model = text_to_model(selected_assessment, models)

    return model
