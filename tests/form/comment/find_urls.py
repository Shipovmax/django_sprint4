import re
from typing import Sequence, Tuple

import django.test
from conftest import KeyVal, get_page_context_form
from django.http import HttpResponse
from django.urls import NoReverseMatch
from fixtures.types import CommentModelAdapterT
from form.find_urls import find_links_between_lines, get_url_display_names


def find_edit_and_delete_urls(
    adapted_comments: Sequence[CommentModelAdapterT],
    post_page_response: HttpResponse,
    urls_start_with: KeyVal,
    user_client: django.test.Client,
) -> Tuple[KeyVal, KeyVal]:
    """Looks up two links in the post_page_response's content.
    The links must be found between two adjacent comments to the post.
    The link that leads to a page with a form in its template's context
    is the one for edit the comment,
    the other one, therefore, is for its deletion.
    !!! Make sure each comment text in unique on the page.
    """

    post_page_content = post_page_response.content.decode("utf-8")
    assert len(adapted_comments) >= 2

    # Get info about html between two consecutive comments
    pattern = re.compile(
        rf"{adapted_comments[0].text}([\w\W]*?){adapted_comments[1].text}"
    )
    between_comments_match = pattern.search(post_page_content)
    assert between_comments_match, (
        "Ensure that comments k postm otsortirovany po vremeni ikh"
        " post, «ot starykh k novym»."
    )
    text_between_comments = between_comments_match.group(1)
    between_comments_start_lineix = post_page_content.count(
        "\n", 0, between_comments_match.start()
    )
    between_comments_end_lineix = between_comments_start_lineix + (
        between_comments_match.group().count("\n")
    )

    comment_links = find_links_between_lines(
        post_page_content,
        urls_start_with.val,
        between_comments_start_lineix,
        between_comments_end_lineix,
        link_text_in=text_between_comments,
    )
    if len(set(link.get("href") for link in comment_links)) != 2:
        raise AssertionError(
            "Ensure that on the post author comment dostupny"
            " links dlya edit i deletion etogo comment. Ssylki"
            " dolzhny vesti na raznye page, adres kotorykh nachinaetsya s"
            f" {urls_start_with.key}"
        )

    # We have two links. Which one of them is the edit link,
    # and which - the delete link? Edit link must lead to a form.

    edit_link, del_link = comment_links[0], comment_links[1]

    def assert_comment_links_return_same_get_status(_comment_links):
        get_request_status_codes = []
        try:
            for comment_link in _comment_links:
                get_request_status_codes.append(
                    user_client.get(comment_link.get("href")).status_code
                )
            return all(
                x == get_request_status_codes[0] for x in get_request_status_codes
            )
        except NoReverseMatch:
            raise AssertionError(
                "Ensure that v kontext shablonov stranits deletion "
                "i edit comment "
                "peredaetsya comment object."
            )
        except Exception:
            return False

    assert assert_comment_links_return_same_get_status(comment_links), (
        "Stranitsy deletion i edit comment dolzhny imet"
        " identichnye prava dostupa. Ensure that GET-zapros k etim pagem"
        " vozvrashchaet odin i tot zhe status i ne udalyaet comments."
    )

    # Make sure GET requests to urls in `comment_links`
    # do not delete the comment (comment & delete are GET-idempotent):
    assert assert_comment_links_return_same_get_status(comment_links), (
        "Ensure that GET-zapros k pagem deletion i edit"
        " comment ne udalyaet comments."
    )

    if get_page_context_form(user_client, comment_links[0].get("href")).key:
        # Found a link leading to a form, let's make sure the other one doesn't
        assert not get_page_context_form(
            user_client, comment_links[1].get("href")
        ).key, (
            "Ensure that v slovar kontexta dlya page deletion"
            " comment ne peredaetsya obekt formy. "
        )
    elif get_page_context_form(user_client, comment_links[1].get("href")).key:
        edit_link, del_link = del_link, edit_link
    else:
        raise AssertionError(
            "Ensure that author comment vidna ssylka na stranitsu"
            " edit etogo comment. Check that v slovar"
            " kontexta dlya page edit comment peredaetsya"
            " obekt formy. "
        )

    comment_url_display_names = get_url_display_names(
        urls_start_with,
        adapted_comments[0].id,
        comment_links,
    )
    edit_url = edit_link.get("href")
    del_url = del_link.get("href")
    return (
        KeyVal(key=edit_url, val=comment_url_display_names[edit_url]),
        KeyVal(key=del_url, val=comment_url_display_names[del_url]),
    )
