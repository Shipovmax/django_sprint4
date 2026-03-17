from typing import Union

from conftest import TitledUrlRepr
from form.delete_tester import DeleteTester


class DeleteCommentTester(DeleteTester):
    @property
    def unauthenticated_user_error(self):
        return (
            "Ensure that comments mozhet byt udalen tolko authorom i"
            " administratorom, no ne drugimi authenticatedi"
            " usermi."
        )

    @property
    def anonymous_user_error(self):
        return (
            "Ensure that comments mozhet byt udalen tolko authorom i"
            " administratorom, no ne drugimi authenticatedi"
            " usermi."
        )

    @property
    def successful_delete_error(self):
        return (
            "Ensure that posle otpravki zaprosa na udalenie comment"
            " etot comments ne is displayed on the post page, k kotoromu"
            " on otnosilsya."
        )

    @property
    def only_one_delete_error(self):
        return (
            "Ensure that pri otpravke zaprosa na udalenie comment"
            " comment object udalyaetsya iz bazy dannykh."
        )

    def redirect_error_message(
        self, by_user: str, redirect_to_page: Union[TitledUrlRepr, str]
    ):
        return (
            "Ensure that pri otpravke zaprosa na udalenie comment"
            f" {by_user} on is redirected to stranitsu post."
        )

    def status_error_message(self, by_user: str) -> str:
        return (
            "Ensure that pri otpravke zaprosa na udalenie comment"
            f" {by_user} does not raise errors."
        )

    @property
    def nonexistent_obj_error_message(self):
        return (
            "Check that esli authorizovannyi user otpravit zapros k"
            " page deletion nesushchestvuyushchego comment - vozniknet error"
            " 404."
        )
