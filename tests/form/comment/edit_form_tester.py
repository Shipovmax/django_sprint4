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
    UnauthorizedEditException,
    UnauthenticatedEditException,
    AuthenticatedEditException,
    DatabaseCreationException,
    ItemCreatedException,
)


class EditCommentFormTester(BaseFormTester):
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
                "Ensure that the"
                " `post/<post_id>/edit_comment/<comment_id>/` peredaetsya"
                " forma dlya edit comment."
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
                "Ensure that v comment edit form est"
                " element `textarea` s textom comment."
            ) from e

    def _validate(self):
        try:
            super()._validate()
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the"
                " `post/<post_id>/edit_comment/<comment_id>/` peredaetsya"
                " forma dlya edit comment."
            ) from e
        except FormMethodException as e:
            raise AssertionError(
                "Ensure that forma dlya edit comment"
                " is submitted using method `POST`."
            ) from e
        except TextareaMismatchException as e:
            raise AssertionError(
                "Ensure that v comment edit form text"
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
                "When edit comment voznikaet error:\n"
                f"{type(e).__name__}: {e}"
            ) from e

    def test_unlogged_cannot_create(
        self, form: BaseForm, qs: QuerySet
    ) -> None:
        try:
            super().test_unlogged_cannot_create(form, qs)
        except ItemCreatedException as e:
            raise AssertionError(
                "Ubedites v tom, chto esli an unauthenticated user"
                " otpravit formu edit comment - obekt"
                " comment v database is not created ili izmenen."
            ) from e

    def test_edit_item(
        self, updated_form: BaseForm, qs: QuerySet, item_adapter: ModelAdapterT
    ) -> HttpResponse:
        try:
            return super().test_edit_item(updated_form, qs, item_adapter)
        except UnauthorizedEditException:
            raise AssertionError(
                "Ensure that an authenticated user ne mozhet"
                " redaktirovat chuzhie comments."
            )
        except UnauthenticatedEditException:
            raise AssertionError(
                "Ensure that an unauthenticated user ne mozhet"
                " redaktirovat comments."
            )
        except AuthenticatedEditException:
            raise AssertionError(
                "Ensure that an authenticated user mozhet"
                " redaktirovat svoi comments."
            )
        except DatabaseCreationException:
            raise AssertionError(
                "Ensure that pri redaktirovanii comment v database"
                " ne sozdaetsya novyi comment object."
            )

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ) -> str:
        redirect_to_page_repr = self.get_redirect_to_page_repr(
            redirect_to_page
        )
        return (
            "Ensure that pri otpravke formy edit comment"
            f" {by_user} on is redirected to {redirect_to_page_repr}."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke formy edit comment"
            f" {by_user} does not raise errors."
        )

    @property
    def author_assignment_error_message(self) -> str:
        return (
            "Ensure that pri redaktirovanii comment v field \"author\""
            " the authenticated user is provided."
        )

    @property
    def display_text_error_message(self) -> str:
        return (
            "Ensure that posle edit comment novyi text"
            " comment is displayed on the post page."
        )

    def validation_error_message(self, student_form_fields_str: str) -> str:
        return (
            "Ensure that dlya validation formy edit comment"
            f" it is enough to fill in the following fields: {student_form_fields_str}."
        )

    @property
    def item_not_created_assertion_msg(self):
        return (
            "Ensure that pri otpravke an authorized user formy"
            " edit comment v database ne sozdaetsya novyi"
            " comment object."
        )

    @property
    def wrong_author_assertion_msg(self):
        return (
            "Ensure that pri redaktirovanii comment v formu v field"
            " «author» the authenticated user is provided."
        )

    def creation_assertion_msg(self, prop):
        return (
            "Ensure that pri sozdanii comment pravilno nastroena"
            f" redirect, i znachenie polya `{prop}` is displayed on the"
            " post page, k kotoromu otnositsya comments."
        )
