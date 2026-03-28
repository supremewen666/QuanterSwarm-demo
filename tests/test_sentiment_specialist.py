from quanter_swarm.agents.specialists import SentimentSpecialist


def test_sentiment_specialist_scores_text() -> None:
    assert SentimentSpecialist().score("positive") == 0.5
