import pytest

from config.staging import datasets


class TestSampleQuestions:
    @pytest.mark.parametrize(
        "dataset, question",
        [
            (dataset, question)
            for dataset in datasets
            for question in dataset.sample_questions
        ],
    )
    def test_answer_user_query(self, dataset, question):
        # TODO: Implement this test
        pass
