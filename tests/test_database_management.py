"""Database tests with mocked repositories, HTTP calls, and a network guard."""

import json
import os
import unittest
from dataclasses import asdict
from unittest.mock import Mock, call, patch

import requests

from Data.NPC import NPC
from Data.Weapon import Weapon
from DatabaseManagement.NpcDB import NpcDB
from DatabaseManagement.WeaponDB import WeaponDB
from DatabaseManagement.Notion.NotionClient import NotionClient
from DatabaseManagement.Notion.NotionProperties import RichTextProperty, TitleProperty
from DatabaseManagement.Notion.RichText import Annotations, RichText, Text
from tests.test_data import npc_data, npc_payload, weapon_data


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        # A missed HTTP mock must fail locally rather than reach a real database.
        guard = patch("requests.sessions.Session.request",
                      side_effect=AssertionError("Real HTTP calls are forbidden in unit tests"))
        self.network_guard = guard.start()
        self.addCleanup(guard.stop)


class RepositoryChecks:
    """Shared test cases executed independently for NPC and weapon repositories."""

    def setUp(self):
        super().setUp()
        factory = patch(self.client_path, autospec=True)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        self.client = self.factory.return_value
        self.repository = self.repository_type()

    def make_model(self):
        return self.model_type(**self.model_data())

    def make_page(self, payload, page_id="page-1"):
        return {"id": page_id, "properties": {self.property_name: {
            "rich_text": [{"plain_text": json.dumps(payload)}]}}}

    def test_constructor(self):
        # Verify construction uses the mocked client and the correct database ID.
        self.factory.assert_called_once_with()
        self.assertIs(self.repository.client, self.client)
        self.assertEqual(self.repository.db_id, self.database_id)

    def test_get_all_empty(self):
        # Verify an empty database response produces an empty model list.
        self.client.get_pages.return_value = []
        self.assertEqual(self.repository.get_all(), [])
        self.client.get_pages.assert_called_once_with(self.database_id)

    def test_get_all_converts_pages_and_assigns_ids(self):
        # Verify page JSON reaches the model reader in order and page IDs override stored IDs.
        payloads = [{"name": "First"}, {"name": "Second"}]
        models = [self.make_model(), self.make_model()]
        self.client.get_pages.return_value = [self.make_page(p, f"page-{i}")
                                             for i, p in enumerate(payloads)]
        with patch.object(self.model_type, "from_dict", side_effect=models) as reader:
            result = self.repository.get_all()
        self.assertEqual(result, models)
        self.assertEqual([item.id for item in result], ["page-0", "page-1"])
        self.assertEqual(reader.call_args_list, [call(p) for p in payloads])
        self.client.get_pages.assert_called_once_with(self.database_id)

    def test_get_all_invalid_page_shapes(self):
        # Verify missing IDs, properties, text fields, and empty text lists are rejected.
        valid = self.make_page({})
        without_id = dict(valid)
        del without_id["id"]
        cases = [({}, KeyError), ({"properties": {}}, KeyError),
                 ({"properties": {self.property_name: {}}}, KeyError),
                 ({"properties": {self.property_name: {"rich_text": []}}}, IndexError),
                 ({"properties": {self.property_name: {"rich_text": [{}]}}}, KeyError),
                 (without_id, KeyError)]
        for page, error in cases:
            with self.subTest(page=page):
                self.client.get_pages.return_value = [page]
                with patch.object(self.model_type, "from_dict", return_value=self.make_model()):
                    with self.assertRaises(error):
                        self.repository.get_all()

    def test_get_all_invalid_json(self):
        # Verify malformed stored JSON raises a decoding error before model construction.
        page = self.make_page({})
        page["properties"][self.property_name]["rich_text"][0]["plain_text"] = "{broken"
        self.client.get_pages.return_value = [page]
        with patch.object(self.model_type, "from_dict") as reader:
            with self.assertRaises(json.JSONDecodeError):
                self.repository.get_all()
            reader.assert_not_called()

    def test_get_all_invalid_model_payload(self):
        # Verify a syntactically valid but incomplete stored model raises KeyError.
        self.client.get_pages.return_value = [self.make_page({})]
        with self.assertRaises(KeyError):
            self.repository.get_all()

    def test_get_all_invalid_response_container(self):
        # Verify a null response cannot be iterated as a collection of pages.
        self.client.get_pages.return_value = None
        with self.assertRaises(TypeError):
            self.repository.get_all()

    def test_add_and_update_properties(self):
        # Verify writes pass the model title and JSON in the correct Notion property format.
        for method in ("add_new", "update"):
            with self.subTest(method=method):
                model = self.make_model()
                model.id = "page-42"
                getattr(self.repository, method)(model)
                writer = self.client.add_page if method == "add_new" else self.client.update_page
                identifier = self.database_id if method == "add_new" else model.id
                writer.assert_called_once()
                actual_id, properties = writer.call_args.args
                self.assertEqual(actual_id, identifier)
                self.assertEqual(set(properties), {"Name", self.property_name})
                self.assertEqual(properties["Name"]["type"], "title")
                self.assertEqual(properties["Name"]["title"][0]["text"]["content"], model.name)
                rich = properties[self.property_name]
                self.assertEqual(rich["type"], "rich_text")
                self.assertEqual(json.loads(rich["rich_text"][0]["text"]["content"]), asdict(model))

    def test_delete(self):
        # Verify deleting a model delegates its page ID to the mocked client exactly once.
        model = self.make_model()
        model.id = "page-42"
        self.repository.delete(model)
        self.client.delete_page.assert_called_once_with("page-42")

    def test_invalid_model_input_prevents_writes(self):
        # Verify null or unrelated model inputs fail before any database write is attempted.
        for method in ("add_new", "update", "delete"):
            for value in (None, {}, "invalid"):
                with self.subTest(method=method, value=value), self.assertRaises(AttributeError):
                    getattr(self.repository, method)(value)
        self.client.add_page.assert_not_called()
        self.client.update_page.assert_not_called()
        self.client.delete_page.assert_not_called()

    def test_serialization_error_prevents_writes(self):
        # Verify model serialization errors stop add and update before reaching the client.
        model = self.make_model()
        with patch.object(self.model_type, "to_json", side_effect=TypeError("Bad model")):
            for method in ("add_new", "update"):
                with self.subTest(method=method), self.assertRaises(TypeError):
                    getattr(self.repository, method)(model)
        self.client.add_page.assert_not_called()
        self.client.update_page.assert_not_called()

    def test_client_errors_propagate(self):
        # Verify every repository operation propagates a simulated client connection error.
        for method, client_method in (("get_all", "get_pages"), ("add_new", "add_page"),
                                      ("update", "update_page"), ("delete", "delete_page")):
            error = requests.ConnectionError("Mock database unavailable")
            getattr(self.client, client_method).side_effect = error
            with self.subTest(method=method), self.assertRaises(requests.ConnectionError) as raised:
                args = () if method == "get_all" else (self.make_model(),)
                getattr(self.repository, method)(*args)
            self.assertIs(raised.exception, error)

    def test_empty_page_id_is_currently_forwarded(self):
        # Document that update and delete currently forward an empty ID without validation.
        model = self.make_model()
        model.id = ""
        self.repository.update(model)
        self.assertEqual(self.client.update_page.call_args.args[0], "")
        self.repository.delete(model)
        self.client.delete_page.assert_called_once_with("")


class NpcDBTests(RepositoryChecks, OfflineTestCase):
    repository_type = NpcDB
    model_type = NPC
    model_data = staticmethod(npc_data)
    client_path = "DatabaseManagement.NpcDB.NotionClient"
    property_name = "Npc"
    database_id = "3e77e8e3bc9980c29effd705e2457f7a"

    def test_get_all_with_real_model_deserialization(self):
        # Verify a valid stored NPC is deserialized and given its Notion page ID.
        self.client.get_pages.return_value = [self.make_page(npc_payload(), "npc-42")]
        result = self.repository.get_all()
        expected = NPC(**npc_data())
        expected.id = "npc-42"
        self.assertEqual(result, [expected])

    def test_picture_placeholders_do_not_call_database(self):
        # Document that unimplemented picture methods return None and make no client calls.
        self.assertIsNone(self.repository.attach_picture(self.make_model()))
        self.assertIsNone(self.repository.upload_picture(None))
        self.assertEqual(self.client.mock_calls, [])


class WeaponDBTests(RepositoryChecks, OfflineTestCase):
    repository_type = WeaponDB
    model_type = Weapon
    model_data = staticmethod(weapon_data)
    client_path = "DatabaseManagement.WeaponDB.NotionClient"
    property_name = "weapon"
    database_id = "3e67e8e3bc99800ca62ec501c9b02016"

    @unittest.expectedFailure
    def test_get_all_with_real_model_deserialization(self):
        # Verify valid stored weapons deserialize; currently blocked by Weapon.from_dict's missing arguments.
        model = self.make_model()
        self.client.get_pages.return_value = [self.make_page(json.loads(model.to_json()), "weapon-42")]
        result = self.repository.get_all()
        model.id = "weapon-42"
        self.assertEqual(result, [model])


class NotionClientTests(OfflineTestCase):
    def setUp(self):
        super().setUp()
        environment = patch.dict(os.environ, {"NOTION_TOKEN": "unit-test-token"})
        environment.start()
        self.addCleanup(environment.stop)
        self.http = {}
        for method in ("post", "get", "patch"):
            mocker = patch(f"DatabaseManagement.Notion.NotionClient.requests.{method}")
            self.http[method] = mocker.start()
            self.addCleanup(mocker.stop)
        self.client = NotionClient()
        self.headers = {"Authorization": "Bearer unit-test-token",
                        "Content-Type": "application/json", "Notion-Version": "2022-02-22"}

    def response(self, data):
        return Mock(json=Mock(return_value=data))

    def operations(self):
        return [("get_pages", "post", ("db-1",)),
                ("get_page", "get", ("db-1", "page-1")),
                ("add_page", "post", ("db-1", {"Name": "Example"})),
                ("update_page", "patch", ("page-1", {"Name": "Example"})),
                ("delete_page", "patch", ("page-1",))]

    def test_constructor_headers(self):
        # Verify the fake token and required API headers are set without making HTTP calls.
        self.assertEqual(self.client.headers, self.headers)
        for http in self.http.values():
            http.assert_not_called()

    def test_missing_token(self):
        # Verify construction without a token raises KeyError before any HTTP request.
        with patch.dict(os.environ):
            os.environ.pop("NOTION_TOKEN", None)
            with self.assertRaises(KeyError) as error:
                NotionClient()
        self.assertEqual(error.exception.args, ("NOTION_TOKEN",))
        for http in self.http.values():
            http.assert_not_called()

    def test_empty_token_is_not_validated(self):
        # Document that an empty token currently produces an empty Bearer credential.
        with patch.dict(os.environ, {"NOTION_TOKEN": ""}):
            self.assertEqual(NotionClient().headers["Authorization"], "Bearer ")

    def test_get_pages_single_response(self):
        # Verify a single query uses a page size of 100 and returns its results, including an empty list.
        for results in ([], [{"id": "page-1"}]):
            with self.subTest(results=results):
                self.http["post"].reset_mock()
                self.http["post"].return_value = self.response({"results": results, "has_more": False})
                self.assertEqual(self.client.get_pages("db-1"), results)
                self.http["post"].assert_called_once_with(
                    "https://api.notion.com/v1/databases/db-1/query",
                    json={"page_size": 100}, headers=self.headers)

    def test_get_pages_pagination(self):
        # Verify all result pages are combined in order and each follow-up uses the returned cursor.
        self.http["post"].side_effect = [
            self.response({"results": [{"id": "one"}], "has_more": True, "next_cursor": "cursor-1"}),
            self.response({"results": [{"id": "two"}], "has_more": True, "next_cursor": "cursor-2"}),
            self.response({"results": [{"id": "three"}], "has_more": False}),
        ]
        self.assertEqual(self.client.get_pages("db-1"), [{"id": "one"}, {"id": "two"}, {"id": "three"}])
        url = "https://api.notion.com/v1/databases/db-1/query"
        self.assertEqual(self.http["post"].call_args_list, [
            call(url, json={"page_size": 100}, headers=self.headers),
            call(url, json={"page_size": 100, "start_cursor": "cursor-1"}, headers=self.headers),
            call(url, json={"page_size": 100, "start_cursor": "cursor-2"}, headers=self.headers)])

    def test_get_pages_explicit_limit(self):
        # Verify an explicit limit is sent unchanged and prevents fetching subsequent pages.
        self.http["post"].return_value = self.response(
            {"results": [{"id": "one"}], "has_more": True, "next_cursor": "unused"})
        self.assertEqual(self.client.get_pages("db-1", 2), [{"id": "one"}])
        self.http["post"].assert_called_once_with(
            "https://api.notion.com/v1/databases/db-1/query", json={"page_size": 2}, headers=self.headers)

    def test_invalid_page_limits_are_forwarded(self):
        # Document that zero, negative, oversized, and nonnumeric limits have no local validation.
        for limit in (0, -1, 101, "invalid"):
            with self.subTest(limit=limit):
                self.http["post"].return_value = self.response({"results": [], "has_more": False})
                self.assertEqual(self.client.get_pages("db-1", limit), [])
                self.assertEqual(self.http["post"].call_args.kwargs["json"], {"page_size": limit})

    def test_get_pages_invalid_response(self):
        # Verify malformed query responses fail for missing keys or invalid container types.
        for data, error in (({}, KeyError), ({"results": []}, KeyError),
                            ({"results": [], "has_more": True}, KeyError), (None, TypeError)):
            with self.subTest(data=data):
                self.http["post"].return_value = self.response(data)
                with self.assertRaises(error):
                    self.client.get_pages("db-1")

    def test_get_page(self):
        # Verify fetching one page uses the page ID endpoint and returns the mocked response.
        data = {"object": "page", "id": "page-1"}
        self.http["get"].return_value = self.response(data)
        self.assertEqual(self.client.get_page("db-1", "page-1"), data)
        self.http["get"].assert_called_once_with(
            "https://api.notion.com/v1/pages/page-1", headers=self.headers)

    def test_write_requests(self):
        # Verify create, update, and delete send the expected URLs, payloads, and headers.
        properties = {"Name": {"title": []}}
        data = {"object": "page", "id": "page-1"}
        for http in self.http.values():
            http.return_value = self.response(data)
        self.assertEqual(self.client.add_page("db-1", properties), data)
        self.http["post"].assert_called_once_with("https://api.notion.com/v1/pages",
            json={"parent": {"database_id": "db-1", "type": "database_id"}, "properties": properties},
            headers=self.headers)
        self.assertEqual(self.client.update_page("page-1", properties), data)
        self.assertEqual(self.client.delete_page("page-1"), data)
        self.assertEqual(self.http["patch"].call_args_list, [
            call("https://api.notion.com/v1/pages/page-1", json={"properties": properties}, headers=self.headers),
            call("https://api.notion.com/v1/pages/page-1", json={"in_trash": True}, headers=self.headers)])

    def test_api_errors_are_returned_and_printed(self):
        # Verify failed writes return the mocked API error and print its code and message.
        data = {"object": "error", "code": "validation_error", "message": "Invalid input"}
        for method, verb, args in self.operations()[2:]:
            with self.subTest(method=method), patch("builtins.print") as output:
                self.http[verb].return_value = self.response(data)
                self.assertEqual(getattr(self.client, method)(*args), data)
                self.assertEqual(output.call_args_list,
                                 [call("validation_error"), call("\n"), call("Invalid input")])

    def test_invalid_write_responses(self):
        # Verify write responses without an object discriminator fail with KeyError.
        for method, verb, args in self.operations()[2:]:
            with self.subTest(method=method):
                self.http[verb].return_value = self.response({})
                with self.assertRaises(KeyError):
                    getattr(self.client, method)(*args)

    def test_transport_errors(self):
        # Verify every API operation propagates mocked connection errors and timeouts.
        for method, verb, args in self.operations():
            for error_type in (requests.ConnectionError, requests.Timeout):
                with self.subTest(method=method, error_type=error_type):
                    error = error_type("Simulated HTTP failure")
                    self.http[verb].side_effect = error
                    with self.assertRaises(error_type) as raised:
                        getattr(self.client, method)(*args)
                    self.assertIs(raised.exception, error)
            self.http[verb].side_effect = None

    def test_invalid_response_json(self):
        # Verify every API operation propagates a mocked response JSON decoding error.
        for method, verb, args in self.operations():
            with self.subTest(method=method):
                response = Mock()
                response.json.side_effect = json.JSONDecodeError("Invalid JSON", "{", 0)
                self.http[verb].return_value = response
                with self.assertRaises(json.JSONDecodeError):
                    getattr(self.client, method)(*args)

    def test_invalid_write_inputs_are_forwarded(self):
        # Document that null properties and empty identifiers are forwarded without local validation.
        self.http["post"].return_value = self.response({"object": "page"})
        self.http["patch"].return_value = self.response({"object": "page"})
        self.client.add_page("", None)
        self.assertEqual(self.http["post"].call_args.kwargs["json"],
                         {"parent": {"database_id": "", "type": "database_id"}, "properties": None})
        self.client.update_page("", None)
        self.assertEqual(self.http["patch"].call_args.args[0], "https://api.notion.com/v1/pages/")
        self.assertEqual(self.http["patch"].call_args.kwargs["json"], {"properties": None})

    def test_invalid_read_identifiers_are_forwarded(self):
        # Document that empty and null database/page IDs are formatted into URLs without validation.
        for identifier in ("", None):
            with self.subTest(identifier=identifier):
                self.http["post"].return_value = self.response({"results": [], "has_more": False})
                self.client.get_pages(identifier)
                self.assertEqual(self.http["post"].call_args.args[0],
                                 f"https://api.notion.com/v1/databases/{identifier}/query")
                self.http["get"].return_value = self.response({"object": "error"})
                self.assertEqual(self.client.get_page("unused", identifier), {"object": "error"})
                self.assertEqual(self.http["get"].call_args.args[0],
                                 f"https://api.notion.com/v1/pages/{identifier}")


class NotionPropertyTests(OfflineTestCase):
    def test_text_fields(self):
        # Verify text content, default null link, and an explicitly supplied link are preserved.
        self.assertEqual(asdict(Text("Example")), {"content": "Example", "link": None})
        self.assertEqual(asdict(Text("", "https://example.test")),
                         {"content": "", "link": "https://example.test"})

    def test_text_requires_content(self):
        # Verify constructing a Text without content raises TypeError.
        with self.assertRaises(TypeError):
            Text()

    def test_annotation_defaults_and_overrides(self):
        # Verify all annotation flags default to false and explicit formatting is preserved.
        expected = dict(bold=False, italic=False, strikethrough=False, underline=False,
                        code=False, color="default")
        self.assertEqual(asdict(Annotations()), expected)
        self.assertEqual(asdict(Annotations(True, True, True, True, True, "red")),
                         dict.fromkeys(expected.keys() - {"color"}, True) | {"color": "red"})

    def test_rich_text_content(self):
        # Verify rich text wraps normal, empty, Unicode, and multiline content with default annotations.
        for value in ("Example", "", "\u6012\u308a", "First\nSecond"):
            with self.subTest(value=value):
                rich = RichText(value)
                self.assertEqual(rich.text.content, value)
                self.assertEqual(rich.plainText, value)
                self.assertEqual(rich.type, "text")
                self.assertEqual(rich.annotations, Annotations())

    def test_rich_text_annotations_are_independent(self):
        # Verify changing one rich text object's annotations does not change another object's defaults.
        first, second = RichText("First"), RichText("Second")
        first.annotations.bold = True
        self.assertFalse(second.annotations.bold)
        self.assertIsNot(first.text, second.text)

    def test_property_serialization(self):
        # Verify title and rich text properties serialize their type and nested text content.
        for cls, key in ((TitleProperty, "title"), (RichTextProperty, "rich_text")):
            for value in ("Example", "", "\u6012\u308a"):
                with self.subTest(cls=cls, value=value):
                    result = asdict(cls(value))
                    self.assertEqual(result["type"], key)
                    self.assertEqual(len(result[key]), 1)
                    self.assertEqual(result[key][0]["text"], {"content": value, "link": None})
                    self.assertEqual(result[key][0]["annotations"], asdict(Annotations()))

    def test_property_lists_are_independent(self):
        # Verify title and rich text wrappers do not share their mutable text lists.
        for cls, key in ((TitleProperty, "title"), (RichTextProperty, "rich_text")):
            with self.subTest(cls=cls):
                first, second = cls("First"), cls("Second")
                getattr(first, key).append(RichText("Extra"))
                self.assertEqual(len(getattr(second, key)), 1)

    def test_required_text_arguments(self):
        # Verify rich text and both property wrappers require their input text argument.
        for cls in (RichText, TitleProperty, RichTextProperty):
            with self.subTest(cls=cls), self.assertRaises(TypeError):
                cls()

    def test_invalid_content_types_are_not_validated(self):
        # Document that text wrappers currently accept null and numeric content without validation.
        for value in (None, 123):
            with self.subTest(value=value):
                self.assertEqual(Text(value).content, value)
                self.assertEqual(RichText(value).text.content, value)
                self.assertEqual(TitleProperty(value).title[0].text.content, value)
                self.assertEqual(RichTextProperty(value).rich_text[0].text.content, value)
        self.assertEqual(Annotations(bold="invalid", color=123).bold, "invalid")

    @unittest.expectedFailure
    def test_rich_text_serialized_plain_text(self):
        # Verify serialized plain_text matches content; currently __init__ assigns plainText instead.
        self.assertEqual(asdict(RichText("Example"))["plain_text"], "Example")

    @unittest.expectedFailure
    def test_rich_text_missing_href_is_null(self):
        # Verify an absent href serializes as JSON null; currently it is the literal string "null".
        self.assertIsNone(asdict(RichText("Example"))["href"])


if __name__ == "__main__":
    unittest.main()
