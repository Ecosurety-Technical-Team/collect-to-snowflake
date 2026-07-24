def pascal_case_to_upper_case(s: str) -> str:
    words: list[str] = []
    word: list[str] = []

    clean_s = s.replace("ID", "Id")

    for index, c in enumerate(clean_s):
        if c == ".":
            if word:
                words.append("".join(word))
                word = []
            continue

        previous = clean_s[index - 1] if index else ""
        following = clean_s[index + 1] if index + 1 < len(clean_s) else ""
        starts_word = (
            c.isupper()
            and word
            and (
                previous.islower()
                or previous.isdigit()
                or (previous.isupper() and following.islower())
            )
        )

        if starts_word:
            words.append("".join(word))
            word = []

        word.append(c)

    if word:
        words.append("".join(word))

    return "_".join(word.upper() for word in words)
