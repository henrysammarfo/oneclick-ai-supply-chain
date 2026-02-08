from agents.buyer_agent import BuyerAgent


class DummyMsg:
    content = "ok"


class DummyChoice:
    message = DummyMsg()


class DummyResp:
    choices = [DummyChoice()]


def test_extract_content_handles_string_and_openai():
    buyer = BuyerAgent("Test")
    assert buyer._extract_content("hello") == "hello"
    assert buyer._extract_content(DummyResp()) == "ok"
