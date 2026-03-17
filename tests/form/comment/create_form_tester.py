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
    BaseFormTester,
    ItemCreatedException,
)


class CreateCommentFormTester(BaseFormTester):
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
                "Ensure that dlya authenticated user na"
                " stranitsu post form is provided dlya create comment."
            ) from e

    @property
    def has_textarea(self):
        return True

    @property
    def textarea_tag(self) -> bs4.Tag:
        try:
            return super().textarea_tag
        except TextareaTagMissingException as e:
            raise AssertionError(
                "Ensure that v forme dlya create comment est field"
                " tipa `textarea` dlya vvoda texta."
            ) from e

    def _validate(self):
        try:
            super()._validate()
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that dlya authenticated user na"
                " stranitsu post form is provided dlya create comment."
            ) from e
        except FormMethodException as e:
            raise AssertionError(
                "Ensure that the comment create form otpravlyaetsya"
                " metodom `POST`."
            ) from e
        except TextareaMismatchException as e:
            raise AssertionError(
                "Ensure that v comment create form text"
                " comment peredaetsya cherez field tipa `textarea`."
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
                "When creating comment voznikaet error:\n"
                f"{type(e).__name__}: {e}"
            ) from e

    def test_unlogged_cannot_create(
        self, form: BaseForm, qs: QuerySet
    ) -> None:
        try:
            super().test_unlogged_cannot_create(form, qs)
        except ItemCreatedException as e:
            raise AssertionError(
                "Ensure that pri otpravke comment"
                " neauthenticated userem v database ne"
                " sozdaetsya comment object."
            ) from e

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ) -> str:
        redirect_to_page_repr = self.get_redirect_to_page_repr(
            redirect_to_page
        )
        return (
            "Ensure that pri otpravke formy create comment"
            f" {by_user} on is redirected to {redirect_to_page_repr}."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke formy dlya create comment"
            f" {by_user} does not raise errors."
        )

    @property
    def author_assignment_error_message(self) -> str:
        return (
            "Ensure that pri sozdanii comment v formu v `author` field"
            " the authenticated user is provided."
        )

    @property
    def display_text_error_message(self) -> str:
        return (
            "Ensure that posle sozdanii comment ego text is displayed"
            " on the post page v spiske kommentariev."
        )

    def validation_error_message(self, student_form_fields_str: str) -> str:
        return (
            "Ensure that dlya validation formy create comment"
            f" it is enough to fill in the following fields: {student_form_fields_str}."
        )

    @property
    def item_not_created_assertion_msg(self):
        return (
            "Ensure that pri otpravke formy create comment"
            " an authorized user v database sozdaetsya odin i"
            " tolko odin comment object."
        )

    @property
    def wrong_author_assertion_msg(self):
        return (
            "Ensure that pri sozdanii comment v formu v `author` field"
            " the authenticated user is provided."
        )

    def creation_assertion_msg(self, prop):
        return (
            "Ensure that pri sozdanii comment pravilno nastroena"
            f" redirect, i znachenie polya `{prop}` is displayed on the"
            " post page, k kotoromu otnositsya comments."
        )
