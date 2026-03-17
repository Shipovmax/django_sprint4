from typing import Tuple, Union

import bs4
from django.db.models import QuerySet, Model
from django.forms import BaseForm
from django.http import HttpResponse

from conftest import TitledUrlRepr
from fixtures.types import ModelAdapterT
from form.base_form_tester import (
    FormTagMissingException,
    FormMethodException,
    TextareaMismatchException,
    TextareaTagMissingException,
)
from form.base_form_tester import (
    SubmitTester,
    FormValidationException,
    ItemCreatedException,
)
from form.post.form_tester import PostFormTester


class CreatePostFormTester(PostFormTester):
    def __init__(
        self,
        response: HttpResponse,
        *args,
        ModelAdapter: ModelAdapterT,
        **kwargs,
    ):
        try:
            super().__init__(
                response, *args, ModelAdapter=ModelAdapter, **kwargs
            )
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the create post form is provided."
            ) from e

    @property
    def textarea_tag(self) -> bs4.Tag:
        try:
            return super().textarea_tag
        except TextareaTagMissingException as e:
            raise AssertionError(
                "Ensure that v post create form est element"
                " `textarea`."
            ) from e

    def _validate(self):
        try:
            super()._validate()
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the create post form is provided."
            ) from e
        except FormMethodException as e:
            raise AssertionError(
                "Ensure that the post create form is submitted using method"
                " `POST`."
            ) from e
        except TextareaMismatchException as e:
            raise AssertionError(
                "Ensure that v post create form text post"
                " is submitted through a `textarea` field."
            ) from e

    def try_create_item(
        self,
        form: BaseForm,
        qs: QuerySet,
        submitter: SubmitTester,
        assert_created: bool = True,
    ) -> Tuple[HttpResponse, Model]:
        try:
            return super().try_create_item(form, qs, submitter, assert_created)
        except FormValidationException as e:
            raise AssertionError(
                "When creating post voznikaet error:\n"
                f"{type(e).__name__}: {e}"
            ) from e

    def test_unlogged_cannot_create(
        self, form: BaseForm, qs: QuerySet
    ) -> None:
        try:
            super().test_unlogged_cannot_create(form, qs)
        except ItemCreatedException as e:
            raise AssertionError(
                "Check that esli an unauthenticated user"
                " otpravit formu dlya create post - obekt post v baze"
                " dannykh is not created."
            ) from e

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ) -> str:
        redirect_to_page_repr = self.get_redirect_to_page_repr(
            redirect_to_page
        )
        return (
            f"Ensure that pri otpravke formy create post {by_user} on"
            f" is redirected to {redirect_to_page_repr}."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke formy create post"
            f" {by_user} does not raise errors."
        )

    @property
    def author_assignment_error_message(self) -> str:
        return (
            "Ensure that pri sozdanii post v formu v `author` field"
            " the authenticated user is provided."
        )

    @property
    def display_text_error_message(self) -> str:
        return (
            "Ensure that posle create post text is displayed on the"
            " otdelnoi post page."
        )

    def validation_error_message(self, student_form_fields_str: str) -> str:
        return (
            "Ensure that dlya validation formy create post"
            f" it is enough to fill in the following fields: {student_form_fields_str}."
        )

    @property
    def item_not_created_assertion_msg(self):
        return (
            "Ensure that pri otpravke formy create post authorized"
            " userem v database exactly one object is created"
            " post."
        )

    @property
    def wrong_author_assertion_msg(self):
        return (
            "Ensure that pri sozdanii post v formu v `author` field"
            " the authenticated user is provided."
        )

    def creation_assertion_msg(self, prop):
        return (
            "Ensure that posle otpravki formy create post pravilno"
            f" rabotaet redirect. Check that znachenie polya `{prop}`"
            " is displayed on the page, na kotoruyu byl pereadresovan user."
        )
