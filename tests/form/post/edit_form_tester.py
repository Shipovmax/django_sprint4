from typing import Tuple, Union

import bs4
from conftest import TitledUrlRepr, UrlRepr
from django.db.models import Model, QuerySet
from django.forms import BaseForm
from django.http import HttpResponse
from fixtures.types import ModelAdapterT
from form.base_form_tester import (
    AnonymousSubmitTester,
    AuthenticatedEditException,
    DatabaseCreationException,
    FormMethodException,
    FormTagMissingException,
    FormValidationException,
    ItemCreatedException,
    SubmitTester,
    TextareaMismatchException,
    TextareaTagMissingException,
    UnauthenticatedEditException,
    UnauthorizedEditException,
    UnauthorizedSubmitTester,
)
from form.post.form_tester import PostFormTester


class EditPostFormTester(PostFormTester):
    def __init__(
        self,
        response: HttpResponse,
        *args,
        ModelAdapter: ModelAdapterT,
        **kwargs,
    ):
        try:
            super().__init__(response, *args, ModelAdapter=ModelAdapter, **kwargs)
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the edit post peredaetsya" " forma."
            ) from e

    @property
    def unauthorized_edit_redirect_cbk(self):
        redirect_to_page: TitledUrlRepr = (
            UrlRepr(r"/posts/\d+/$", "/posts/<int:post_id>/"),
            "post page",
        )
        return UnauthorizedSubmitTester.get_test_response_redirect_cbk(
            tester=self, redirect_to_page=redirect_to_page
        )

    @property
    def anonymous_edit_redirect_cbk(self):
        return AnonymousSubmitTester.get_test_response_redirect_cbk(
            tester=self, redirect_to_page="authentication page"
        )

    @property
    def textarea_tag(self) -> bs4.Tag:
        try:
            return super().textarea_tag
        except TextareaTagMissingException as e:
            raise AssertionError(
                "Ensure that v post edit form est element" " `textarea`."
            ) from e

    def _validate(self):
        try:
            super()._validate()
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the edit post peredaetsya" " forma."
            ) from e
        except FormMethodException as e:
            raise AssertionError(
                "Ensure that forma dlya edit post otpravlyaetsya" " metodom `POST`."
            ) from e
        except TextareaMismatchException as e:
            raise AssertionError(
                "Ensure that v post edit form osnovnoi text"
                " peredaetsya v field tipa `textarea`."
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
                "When edit post voznikaet error:\n" f"{type(e).__name__}: {e}"
            ) from e

    def test_unlogged_cannot_create(self, form: BaseForm, qs: QuerySet) -> None:
        try:
            super().test_unlogged_cannot_create(form, qs)
        except ItemCreatedException as e:
            raise AssertionError(
                "Check that esli an unauthenticated user"
                " otpravit formu edit post - obekt post v baze"
                " dannykh is not created ili izmenen."
            ) from e

    def test_edit_item(
        self, updated_form: BaseForm, qs: QuerySet, item_adapter: ModelAdapterT
    ) -> HttpResponse:
        try:
            return super().test_edit_item(updated_form, qs, item_adapter)
        except UnauthorizedEditException:
            raise AssertionError(
                "Ensure that user ne mozhet redaktirovat chuzhie" " posty."
            )
        except UnauthenticatedEditException:
            raise AssertionError(
                "Ensure that an unauthenticated user ne mozhet" " redaktirovat posty."
            )
        except AuthenticatedEditException:
            raise AssertionError("Ensure that user mozhet redaktirovat svoi posty.")
        except DatabaseCreationException:
            raise AssertionError(
                "Ensure that pri redaktirovanii post v database ne"
                " sozdaetsya novyi obekt post."
            )

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ) -> str:
        redirect_to_page_repr = self.get_redirect_to_page_repr(redirect_to_page)
        return (
            "Ensure that pri otpravke formy edit post"
            f" {by_user} on is redirected to {redirect_to_page_repr}."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke formy edit post"
            f" {by_user} does not raise errors."
        )

    @property
    def author_assignment_error_message(self) -> str:
        return (
            "Ensure that v formu edit post v `author` field"
            " the authenticated user is provided."
        )

    @property
    def display_text_error_message(self) -> str:
        return (
            "Ensure that posle edit post novyi text" " is displayed on the post page."
        )

    def validation_error_message(self, student_form_fields_str: str) -> str:
        return (
            "Ensure that dlya validation formy edit post"
            f" it is enough to fill in the following fields: {student_form_fields_str}."
        )

    @property
    def item_not_created_assertion_msg(self):
        return (
            "Ensure that pri otpravke formy edit post"
            " an authorized user  v database ne sozdaetsya novyi"
            " obekt post."
        )

    @property
    def wrong_author_assertion_msg(self):
        return (
            "Ensure that pri redaktirovanii post v formu v `author` field"
            " the authenticated user is provided."
        )

    def creation_assertion_msg(self, prop):
        return (
            "Ensure that posle otpravki formy edit post"
            " redirect works correctly. Check that znachenie polya"
            f" `{prop}` is displayed on the post page."
        )
