from flask import request


def fetch_answers(total_expected_answers):
    form = request.form
    def _get_index(item):
        try:
            key = item[0]
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid answer key '{item[0]}'. Expected format "
                "'answer_<index>'."
            )
        return int(key.split("_")[1])

    for i in range(total_expected_answers - 1):
        try:
            key = f"answer_{i}"
            if key not in form:
                form[key] = None
        except (ValueError, IndexError):
            pass
    sorted_form = dict(sorted(form.items(), key=_get_index))
    # Expecting form values as answers
    sorted_answers = list(sorted_form.values())
    return sorted_answers
