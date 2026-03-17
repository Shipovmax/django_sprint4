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


class EditUserFormTester(BaseFormTester):
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
                "Ensure that the edit the profile"
                " user form is provided."
            ) from e

    @property
    def has_textarea(self):
        return False

    @property
    def textarea_tag(self) -> bs4.Tag:
        raise NotImplementedError(
            "This tag is not applicable on user profile page."
        )

    def _validate(self):
        try:
            super()._validate()
        except FormTagMissingException as e:
            raise AssertionError(
                "Ensure that the edit the profile"
                " user form is provided."
            ) from e
        except FormMethodException as e:
            raise AssertionError(
                "Ensure that forma edit the profile user"
                " is submitted using method `POST`."
            ) from e
        except TextareaMismatchException:
            pass

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
                "When edit the profile user voznikaet error:\n"
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
                " otpravit formu edit the profile - obekt user"
                " v database is not created ili izmenen."
            ) from e

    def test_edit_item(
        self, updated_form: BaseForm, qs: QuerySet, item_adapter: ModelAdapterT
    ) -> HttpResponse:
        try:
            return super().test_edit_item(updated_form, qs, item_adapter)
        except UnauthorizedEditException:
            raise AssertionError(
                "Ensure that user ne mozhet redaktirovat chuzhoi"
                " profil user."
            )
        except UnauthenticatedEditException:
            raise AssertionError(
                "Ensure that an unauthenticated user ne mozhet"
                " redaktirovat profil user."
            )
        except AuthenticatedEditException:
            raise AssertionError(
                "Ensure that user mozhet redaktirovat svoi"
                " profil."
            )
        except DatabaseCreationException:
            raise AssertionError(
                "Ensure that pri redaktirovanii profile user v"
                " database ne sozdaetsya novyi obekt profile user."
            )

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ) -> str:
        redirect_to_page_repr = self.get_redirect_to_page_repr(
            redirect_to_page
        )
        return (
            "Ensure that posle otpravki formy edit the profile"
            f" user {by_user} on is redirected to"
            f" {redirect_to_page_repr}."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke formy edit the profile"
            f" user {by_user} does not raise errors."
        )

    @property
    def author_assignment_error_message(self) -> str:
        return (
            "Ensure that v formu edit the profile user v field"
            " «author» the authenticated user is provided."
        )

    @property
    def display_text_error_message(self) -> str:
        return (
            "Ensure that posle redaktirovanii profile user novyi"
            " text is displayed on the profile page."
        )

    def validation_error_message(self, student_form_fields_str: str) -> str:
        return (
            "Ensure that dlya validation formy edit the profile"
            " user it is enough to fill in the following fields:"
            f" {student_form_fields_str}."
        )

    @property
    def item_not_created_assertion_msg(self):
        return (
            "Ensure that pri otpravke formy edit the profile"
            " user an authorized user v database ne"
            " sozdaetsya novyi profil user."
        )

    @property
    def wrong_author_assertion_msg(self):
        raise NotImplementedError(
            "User profiles are not supposed to be created from code."
        )

    def creation_assertion_msg(self, prop):
        return (
            "Ensure that posle otpravki formy redaktirovanii profile"
            " user pravilno rabotaet  redirect. Check that"
            f" znachenie polya `{prop}` is displayed on the profile page."
        )
