from typing import Union

from conftest import TitledUrlRepr
from form.delete_tester import DeleteTester


class DeletePostTester(DeleteTester):
    @property
    def unauthenticated_user_error(self):
        return (
            "Ensure that post mozhet byt udalen tolko authorom i"
            " administratorom, no ne drugimi authenticatedi"
            " usermi."
        )

    @property
    def anonymous_user_error(self):
        return (
            "Ensure that post ne mozhet byt udalen neauthenticated"
            " userem."
        )

    @property
    def successful_delete_error(self):
        return (
            "Ensure that posle otpravki zaprosa na udalenie post etot post"
            " ne is displayed v spiske postov."
        )

    @property
    def only_one_delete_error(self):
        return (
            "Ensure that pri otpravke zaprosa na udalenie post etot post"
            " udalyaetsya iz bazy dannykh."
        )

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ):
        return (
            "Ensure that pri otpravke zaprosa na udalenie post"
            f" {by_user} on is redirected to home page."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke zaprosa na udalenie post"
            f" {by_user} does not raise errors."
        )

    @property
    def nonexistent_obj_error_message(self):
        return (
            "Ensure that esli authorizovannyi user otpravit zapros k"
            " page deletion nesushchestvuyushchei post, to v otvet on"
            " poluchit oshibku 404."
        )
