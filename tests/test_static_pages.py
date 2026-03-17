def test_static_pages_as_cbv():
    try:
        from pages import urls
    except Exception as e:
        raise AssertionError(
            "Ensure that in the file `pages/urls.py` there are no errors. Pri ego"
            f" importe an error occurred:\n{type(e).__name__}: {e}"
        )
    try:
        from pages.urls import urlpatterns
    except Exception:
        raise AssertionError(
            "Ensure that the `urlpatterns` list is defined in `pages/urls.py`."
        )
    try:
        from pages.urls import app_name
    except Exception:
        raise AssertionError(
            "Ensure that in the file `pages/urls.py` opredelena globalnaya"
            " peremennaya `app_name`, zadayushchaya prostranstvo imen url dlya"
            " applications `pages`."
        )
    for path in urlpatterns:
        if not hasattr(path.callback, "view_class"):
            raise AssertionError(
                "Ensure that in the file `pages/urls.py` marshruty staticheskikh"
                " stranits podklyucheny s pomoshchyu CBV."
            )
