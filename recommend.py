import pandas as pd
import fastwer
import numpy as np
import sys

THRESHOLD = 30
FINE_OLD = 5


def preprocessing(path_markup: str = 'MarkupLibra.csv') -> dict:
    markup = pd.read_csv(path_markup)
    dict_markup = {markup.iloc[idx][0]: markup.iloc[idx][1] for idx in range(markup.shape[0])}
    return dict_markup


def search_idx(text: str, markup: dict, recommend_positions: list) -> list:
    for sequence, idx in markup.items():
        if ' ' in sequence:
            sequence = sequence.split()
            values = [fastwer.score([word], [text], char_level=True) for word in sequence]
            if min(values) < THRESHOLD:
                recommend_positions.append((idx, min(values)))
        else:
            value = fastwer.score([sequence], [text], char_level=True)
            if value < THRESHOLD:
                recommend_positions.append((idx, value))
    return recommend_positions


def recommend(text: str) -> tuple or list:
    markup = preprocessing()
    recommend_positions = []
    if ' ' in text:
        for words in text.split():
            recommend_positions = search_idx(words, markup, recommend_positions)
    else:
        recommend_positions = search_idx(text, markup, recommend_positions)

    list_rec = [i for i, _ in recommend_positions]
    position = [element for element in set(list_rec) if list_rec.count(element) >= 2]
    if position:
        return position[0], np.mean([i for _, i in recommend_positions]) / 2
    if recommend_positions:
        return recommend_positions[0]


def main(request_text: str) -> dict:
    if ' ' in request_text:
        request_sequence = request_text.split()
        result = []
        for start in range(len(request_sequence)):
            value = recommend(' '.join(request_sequence[start: start + 2]))
            if value:
                result.append(value)
        pos_final = set([i for i, _ in result])
        count = list(range(len(pos_final) + 2))
        fine_pos = [FINE_OLD * i for idx_pos, i in zip(pos_final, count)]

        recommendation = {}
        for pos, fine in zip(pos_final, fine_pos):
            recommendation[pos] = sum([i for idx, i in result if idx == pos]) + fine

        return {k: v for k, v in sorted(recommendation.items(), key=lambda item: item[1])}
    else:
        result = recommend(request_text)
        return {result[0]: result[1]}


if __name__ == '__main__':
    # print(main('огурцы'))  # {52: 0.0}
    # print(main('морковка нет лук репчатый хотя надо сначала взвесить огурцы'))  # {52: 5.0, 61: 10.0, 51: 25.0}
    print(main(' '.join(sys.argv[1:])))  # python3 recommend.py имбирь конфеты