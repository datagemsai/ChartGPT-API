from chartbot import run


def test_run():
    dataset_id = "dune_dataset"
    question = "Plot the loan principal amount grouped by protocol (i.e. nftfi, benddao, arcade)"
    questions = [{'question': question}]

    run(questions=questions, dataset_id=dataset_id)
