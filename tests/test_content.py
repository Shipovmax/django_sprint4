import inspect
from abc import abstractmethod, ABC
from typing import Type, Optional, Callable, List, Tuple, Union

import pytest
from bs4 import BeautifulSoup
from bs4.element import SoupStrainer
from django.db.models import Model
from django.http import HttpResponse
from django.test.client import Client
from mixer.main import Mixer

from adapters.model_adapter import ModelAdapter
from adapters.post import PostModelAdapter
from conftest import (
    N_PER_PAGE,
    UrlRepr,
    _testget_context_item_by_class,
    _testget_context_item_by_key,
)

pytestmark = [pytest.mark.django_db]


class ContentTester(ABC):
    n_per_page = N_PER_PAGE

    def __init__(
        self,
        mixer: Mixer,
        item_cls: Type[Model],
        adapter_cls: Type[ModelAdapter],
        user_client: Client,
        page_url: Optional[UrlRepr] = None,
        another_user_client: Optional[Client] = None,
        unlogged_client: Optional[Client] = None,
    ):
        self._mixer = mixer
        self._items_key = None
        self._page_url = page_url
        self.item_cls = item_cls
        self.adapter_cls = adapter_cls
        self.user_client = user_client
        self.another_user_client = another_user_client
        self.unlogged_client = unlogged_client

    @property
    def page_url(self):
        return self._page_url

    @property
    @abstractmethod
    def items_hardcoded_key(self):
        raise NotImplementedError(
            "Override `items_hardcoded_key` property "
            "in ContentTester`s child class"
        )

    @abstractmethod
    def raise_assert_page_loads_cbk(self):
        raise NotImplementedError

    def user_client_testget(
        self,
        url: Optional[str] = None,
        assert_status_in: Tuple[int] = (200,),
        assert_cbk: Union[
            Callable[[], None], str
        ] = "raise_assert_page_loads_cbk",
    ) -> HttpResponse:
        return self._testget(
            self.user_client, url, assert_status_in, assert_cbk
        )

    def another_client_testget(
        self,
        url: Optional[str] = None,
        assert_status_in: Tuple[int] = (200,),
        assert_cbk: Union[
            Callable[[], None], str
        ] = "raise_assert_page_loads_cbk",
    ) -> HttpResponse:
        return self._testget(
            self.another_user_client, url, assert_status_in, assert_cbk
        )

    def _testget(
        self,
        client,
        url: Optional[str] = None,
        assert_status_in: Tuple[int] = (200,),
        assert_cbk: Union[
            Callable[[], None], str
        ] = "raise_assert_page_loads_cbk",
    ) -> HttpResponse:
        url = url or self.page_url.url
        try:
            response = client.get(url)
            if response.status_code not in assert_status_in:
                raise Exception
        except Exception:
            if inspect.isfunction(assert_cbk):
                assert_cbk()
            elif isinstance(assert_cbk, str):
                getattr(self, assert_cbk)()
            else:
                raise AssertionError("Wrong type of `assert_cbk` argument.")

        return response

    @abstractmethod
    def items_key_error_message(self):
        raise NotImplementedError

    @abstractmethod
    def items_hardcoded_key_error_message(self):
        raise NotImplementedError

    @property
    def items_key(self):
        if self._items_key:
            return self._items_key

        def setup_for_url(setup_items: List[Model]) -> UrlRepr:
            temp_category = self._mixer.blend(
                "blog.Category", is_published=True
            )
            temp_location = self._mixer.blend(
                "blog.Location", is_published=True
            )
            temp_post = self._mixer.blend(
                "blog.Post",
                is_published=True,
                location=temp_location,
                category=temp_category,
            )
            setup_items.extend([temp_category, temp_location, temp_post])
            url_repr = self.page_url
            return url_repr

        def teardown(setup_items: List[Model]):
            while setup_items:
                item = setup_items.pop()
                item.delete()

        setup_items = []

        try:
            url_repr = setup_for_url(setup_items)
            context = self.user_client_testget(url=url_repr.url).context
            if self.items_hardcoded_key:
                key_val = _testget_context_item_by_key(
                    context,
                    self.items_hardcoded_key,
                    err_msg=self.items_hardcoded_key_error_message(),
                )
            else:
                key_val = _testget_context_item_by_class(
                    context,
                    self.item_cls,
                    err_msg=self.items_key_error_message(),
                    inside_iter=True,
                )
        finally:
            teardown(setup_items)

        return key_val.key

    def n_or_page_size(self, n: int):
        return min(self.n_per_page, n)


class PostContentTester(ContentTester):
    @property
    def items_hardcoded_key(self):
        return "page_obj"

    @abstractmethod
    def raise_assert_page_loads_cbk(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def image_display_error(self) -> str:
        raise NotImplementedError


class ProfilePostContentTester(PostContentTester):
    def items_key_error_message(self):
        return (
            "Ensure that sushchestvuet rovno odin klyuch, pod kotorym v slovar"
            " kontexta user page peredayutsya post."
        )

    def items_hardcoded_key_error_message(self):
        return (
            "Ensure that v slovar kontexta user page"
            f" post peredayutsya pod klyuchom `{self.items_hardcoded_key}`."
        )

    def raise_assert_page_loads_cbk(self):
        raise AssertionError(
            "Ensure that user page loads without errors."
        )

    @property
    def image_display_error(self) -> str:
        return (
            "Ensure that on the profile authora are displayed"
            " izobrazheniya post."
        )


class MainPostContentTester(PostContentTester):
    def items_key_error_message(self):
        return (
            "Ensure that sushchestvuet rovno odin klyuch, pod kotorym v slovar"
            " kontexta home page peredayutsya post."
        )

    def items_hardcoded_key_error_message(self):
        return (
            "Ensure that v slovar kontexta home page post"
            f" peredayutsya pod klyuchom `{self.items_hardcoded_key}`."
        )

    def raise_assert_page_loads_cbk(self):
        raise AssertionError(
            "Ensure that glavnaya page loads without errors."
        )

    @property
    def image_display_error(self) -> str:
        return (
            "Ensure that on the home page vidny prikreplennye k postm"
            " izobrazheniya."
        )


class CategoryPostContentTester(PostContentTester):
    @property
    def page_url(self):
        if not self._page_url:
            from blog.models import Category

            category = Category.objects.first()
            if category:
                self._page_url = UrlRepr(
                    f"/category/{category.slug}/", "/category/<category_slug>/"
                )
        return self._page_url

    def items_key_error_message(self):
        return (
            "Ensure that sushchestvuet rovno odin klyuch, pod kotorym v slovar"
            " kontexta page category peredayutsya post."
        )

    def items_hardcoded_key_error_message(self):
        return (
            "Ensure that v slovar kontexta page category post"
            f" peredayutsya pod klyuchom `{self.items_hardcoded_key}`."
        )

    def raise_assert_page_loads_cbk(self):
        raise AssertionError(
            "Ensure that page category loads without errors."
        )

    @property
    def image_display_error(self) -> str:
        return (
            "Ensure that on the category vidny prikreplennye k postm"
            " izobrazheniya."
        )


@pytest.fixture
def profile_content_tester(
    user: Model,
    mixer: Mixer,
    PostModel: Type[Model],
    user_client: Client,
    another_user_client: Client,
    unlogged_client: Client,
) -> ProfilePostContentTester:
    url_repr = UrlRepr(f"/profile/{user.username}/", "/profile/<username>/")
    return ProfilePostContentTester(
        mixer,
        PostModel,
        PostModelAdapter,
        user_client,
        url_repr,
        another_user_client,
    )


@pytest.fixture
def main_content_tester(
    user: Model,
    mixer: Mixer,
    PostModel: Type[Model],
    user_client: Client,
    another_user_client: Client,
    unlogged_client: Client,
) -> MainPostContentTester:
    url_repr = UrlRepr("/", "/")
    return MainPostContentTester(
        mixer, PostModel, PostModelAdapter, user_client, url_repr
    )


@pytest.fixture
def category_content_tester(
    user: Model,
    mixer: Mixer,
    PostModel: Type[Model],
    user_client: Client,
    another_user_client: Client,
    unlogged_client: Client,
) -> CategoryPostContentTester:
    return CategoryPostContentTester(
        mixer, PostModel, PostModelAdapter, user_client
    )


class TestContent:
    @pytest.fixture(autouse=True)
    def init(
        self,
        profile_content_tester,
        main_content_tester,
        category_content_tester,
    ):
        self.profile_tester = profile_content_tester
        self.main_tester = main_content_tester
        self.category_tester = category_content_tester

    def test_unpublished(self, unpublished_post_with_published_locations):
        profile_response = self.profile_tester.user_client_testget()
        context_post = profile_response.context.get(
            self.profile_tester.items_key
        )
        expected_n = self.profile_tester.n_or_page_size(
            len(unpublished_post_with_published_locations)
        )
        assert len(context_post) == expected_n, (
            "Ensure that on the user author mozhet videt svoi"
            " posty, snyatye s post."
        )

        response = self.main_tester.user_client_testget()
        try:
            items_key = self.main_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert len(context_post) == 0, (
                "Ensure that on the home page ne are displayed posty, "
                "snyatye s post."
            )

        response = self.category_tester.user_client_testget()
        try:
            items_key = self.category_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert len(context_post) == 0, (
                "Ensure that on the category ne are displayed posty, "
                "snyatye s post."
            )

    def test_only_own_pubs_in_category(
        self, user_client, post_with_published_location,
            post_with_another_category
    ):
        response = self.category_tester.user_client_testget()
        try:
            items_key = self.category_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert (
                len(context_post) == 1
            ), ("Ensure that on the category "
                "ne are displayed post drugikh category.")

    def test_only_own_pubs_in_profile(
            self, user_client, post_with_published_location,
            post_of_another_author
    ):
        response = self.profile_tester.user_client_testget()
        try:
            items_key = self.profile_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert (
                    len(context_post) == 1
            ), ("Ensure that on the user "
                "ne are displayed post drugikh authorov.")

    def test_unpublished_category(
        self, user_client, post_with_unpublished_category
    ):
        profile_response = self.profile_tester.user_client_testget()
        context_post = profile_response.context.get(
            self.profile_tester.items_key
        )
        expected_n = self.profile_tester.n_or_page_size(
            len(post_with_unpublished_category)
        )
        assert len(context_post) == expected_n, (
            "Ensure that on the user author mozhet videt svoi"
            " posty, prinadlezhashchie category, snyatoi s post."
        )

        main_response = self.main_tester.user_client_testget()
        context_post = main_response.context.get(self.main_tester.items_key)
        assert len(context_post) == 0, (
            "Ensure that on the home page ne are displayed posty, "
            "prinadlezhashchie category, snyatoi s post."
        )

        def raise_assert_not_exist_cbk():
            raise AssertionError(
                "Ensure that page category nedostupna, esli category"
                " snyata s post."
            )

        self.category_tester.user_client_testget(
            assert_status_in=(404,), assert_cbk=raise_assert_not_exist_cbk
        )

    def test_future_post(self, user_client, future_post):
        profile_response = self.profile_tester.user_client_testget()
        context_post = profile_response.context.get(
            self.profile_tester.items_key
        )
        expected_n = self.profile_tester.n_or_page_size(len(future_post))
        assert len(context_post) == expected_n, (
            "Ensure that on the user author mozhet videt svoi"
            " otlozhennye post."
        )

        response = self.main_tester.user_client_testget()
        try:
            items_key = self.main_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert (
                len(context_post) == 0
            ), ("Ensure that on the home page "
                "ne are displayed otlozhennye post.")

        response = self.category_tester.user_client_testget()
        try:
            items_key = self.category_tester.items_key
        except AssertionError:
            pass
        else:
            context_post = response.context.get(items_key)
            assert (
                len(context_post) == 0
            ), ("Ensure that on the category "
                "ne are displayed otlozhennye post.")

    def test_pagination(
        self, user_client, many_post_with_published_locations
    ):
        post = many_post_with_published_locations

        assert len(post) > self.profile_tester.n_per_page
        assert len(post) > self.main_tester.n_per_page
        assert len(post) > self.category_tester.n_per_page

        for (
            tester,
            response_get_func,
            ordering_err_msg,
            pagination_err_msg,
        ) in (
            (
                self.profile_tester,
                self.profile_tester.user_client_testget,
                (
                    "Ensure that post peredayutsya v kontext page"
                    " profile authora otsortirovannymi po vremeni ikh"
                    " post, «ot novykh k starym»."
                ),
                (
                    "Ensure that on the profile authora rabotaet"
                    " paginatsiya."
                ),
            ),
            (
                self.profile_tester,
                self.profile_tester.another_client_testget,
                (
                    "Ensure that post peredayutsya v kontext page"
                    " profile authora otsortirovannymi po vremeni ikh"
                    " post, «ot novykh k starym»."
                ),
                (
                    "Ensure that on the profile authora "
                    "paginatsiya rabotaet v sootvetstvii s zadaniem ."
                ),
            ),
            (
                self.main_tester,
                self.main_tester.user_client_testget,
                (
                    "Ensure that post peredayutsya v kontext home"
                    " page otsortirovannymi po vremeni ikh post, «ot"
                    " novykh k starym»."
                ),
                "Ensure that on the home page "
                "paginatsiya rabotaet v sootvetstvii s zadaniem .",
            ),
            (
                self.category_tester,
                self.category_tester.user_client_testget,
                (
                    "Ensure that post peredayutsya v kontext page"
                    " category otsortirovannymi po vremeni ikh post, «ot"
                    " novykh k starym»."
                ),
                "Ensure that on the category "
                "paginatsiya rabotaet v sootvetstvii s zadaniem .",
            ),
        ):
            response = response_get_func()
            context_post = response.context.get(tester.items_key)
            pub_dates = [x.pub_date for x in context_post]
            if pub_dates != sorted(pub_dates, reverse=True):
                raise AssertionError(ordering_err_msg)
            expected_n = tester.n_or_page_size(len(post))
            assert len(context_post) == expected_n, pagination_err_msg

    def test_image_visible(self, user_client, post_with_published_location):
        post = post_with_published_location
        post_adapter = PostModelAdapter(post)

        testers: List[PostContentTester] = [
            self.profile_tester,
            self.main_tester,
            self.category_tester,
        ]
        img_n_with_post_img = {}

        for i, tester in enumerate(testers):
            img_soup_with_post_img = BeautifulSoup(
                tester.user_client_testget().content.decode("utf-8"),
                features="html.parser",
                parse_only=SoupStrainer("img"),
            )
            img_n_with_post_img[i] = len(img_soup_with_post_img)

        post_adapter.image = None
        post_adapter.save()

        for i, tester in enumerate(testers):
            img_soup_without_post_img = BeautifulSoup(
                tester.user_client_testget().content.decode("utf-8"),
                features="html.parser",
                parse_only=SoupStrainer("img"),
            )
            img_n_without_post_img = len(img_soup_without_post_img)
            assert (
                img_n_with_post_img[i] - img_n_without_post_img
            ) == 1, tester.image_display_error
