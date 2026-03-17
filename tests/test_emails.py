from django.conf import settings
from django.core.mail.backends.locmem import EmailBackend


def test_gitignore():
    try:
        with open(
            settings.BASE_DIR / ".." / ".gitignore",
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as fh:
            gitignore = fh.read()
    except Exception as e:
        raise AssertionError(
            "Pri chtenii faila `.gitignore` v korne proekta an error occurred:\n"
            f"{type(e).__name__}: {e}"
        )
    assert "sent_emails/" in gitignore, (
        "Ensure that direktoriya `sent_emails/`, sluzhashchaya dlya khraneniya"
        " e-mail soobshchenii, ukazana in the file `.gitignore` v korne proekta."
    )


def test_email_backend_settings():
    assert hasattr(
        settings, "EMAIL_BACKEND"
    ), "Ensure that v proekte zadana nastroika `EMAIL_BACKEND`."
    assert EmailBackend.__module__ in settings.EMAIL_BACKEND, (
        "Ensure that failovyi bekend dlya otpravki e-mail podklyuchen s"
        " pomoshchyu nastroiki `EMAIL_BACKEND`."
    )
    excpect_email_file = settings.BASE_DIR / "sent_emails"
    assert getattr(settings, "EMAIL_FILE_PATH", "") == excpect_email_file, (
        "Ensure that v nastroike `EMAIL_FILE_PATH` ukazan put `BASE_DIR /"
        " 'sent_emails'`."
    )
