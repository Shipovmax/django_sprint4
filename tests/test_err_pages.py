import importlib
import inspect
import os
import uuid
from importlib import import_module

import pytest
from django.conf import settings
from django.http import HttpRequest
from pytest_django.asserts import assertTemplateUsed


def test_csrf_failure_view():
    csrf_failure_view_setting = getattr(settings, "CSRF_FAILURE_VIEW", "")
    module_name, function_name = csrf_failure_view_setting.rsplit(".", 1)
    csrf_failure_view = None
    try:
        module = import_module(module_name)
        csrf_failure_view = getattr(module, function_name, None)
    except Exception:
        pass
    assert csrf_failure_view, (
        "Ensure that v `settings.py` zadana nastroika `CSRF_FAILURE_VIEW` i"
        " chto ona ukazyvaet na sushchestvuyushchuyu view-funktsiyu."
    )

    request = HttpRequest()
    request.method = "POST"
    request.POST = {}

    try:
        response = csrf_failure_view(request)
    except Exception:
        raise AssertionError(
            f"Ensure that view-funktsiya `{csrf_failure_view_setting}`"
            " rabotaet bez oshibok."
        )
    else:
        csrf_status = 403
        assert response.status_code == csrf_status, (
            f"Ensure that view-funktsiya `{csrf_failure_view_setting}`"
            f" vozvrashchaet status {csrf_status}."
        )


@pytest.mark.django_db
def test_custom_err_handlers(client, user_client):
    err_pages_vs_file_names = {
        404: "404.html",
        403: "403csrf.html",
        500: "500.html",
    }
    for status, fname in err_pages_vs_file_names.items():
        try:
            fpath = settings.TEMPLATES_DIR / "pages" / fname
        except Exception as e:
            raise AssertionError(
                "Ensure that peremennaya TEMPLATES_DIR v project settings "
                "is a string (str) or an object, sootvetstvuyushchim path-like interfeisu "
                "(naprimer, ekzemplyarom pathlib.Path). "
                f'While evaluating konkatenatsii settings.TEMPLATES_DIR / "pages", an error occurred: {e}'
            )
        assert os.path.isfile(
            fpath.resolve()
        ), f"Ensure that the template file `{fpath}` exists."

    try:
        from blogicum.urls import handler500
    except Exception:
        raise AssertionError(
            "Ensure that v golovnom faile s marshrutami there are no errors i chto v"
            " nem zadan obrabotchik errors 500."
        )

    def check_handler_exists(handler_path):
        module_name, func_name = handler_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            return False
        try:
            getattr(module, func_name)
        except AttributeError:
            return False
        return True

    assert check_handler_exists(handler500), (
        "Ensure that obrabotchik errors 500 v golovnom faile s marshrutami "
        "ukazyvaet na sushchestvuyushchuyu funktsiyu."
    )

    try:
        from pages import views as pages_views
    except Exception:
        raise AssertionError(
            "Ensure that in the file `pages/views.py` there are no errors."
        )

    for status, fname in err_pages_vs_file_names.items():
        assert fname in inspect.getsource(pages_views), (
            "Proverte view-funktsii applications `pages`: ubedites, chto dlya"
            " generatsii stranits so statusom otveta `{status}` ispolzuetsya"
            " shablon `pages/{fname}`"
        )

    # test template for 404
    debug = settings.DEBUG
    settings.DEBUG = False

    status = 404
    fname = err_pages_vs_file_names[status]
    non_existing_url = uuid.uuid4()
    expected_template = f"pages/{fname}"
    response = client.get(non_existing_url)
    assertTemplateUsed(
        response,
        expected_template,
        (
            f"Ensure that dlya stranits so statusom otveta `{status}`"
            f" ispolzuetsya shablon `{expected_template}`"
        ),
    )

    settings.DEBUG = debug
