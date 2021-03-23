import pandas as pd
import fastwer
import sys

THRESHOLD = 60
FINE_OLD = 5


def preprocessing(path_markup: str = 'MarkupLibra.csv') -> dict:
    markup = pd.read_csv(path_markup)
    dict_markup = {markup.iloc[idx][0]: markup.iloc[idx][1] for idx in range(markup.shape[0])}
    return dict_markup


def search_idx(text: str, markup: dict, recommend_positions: list) -> list:
    len_text = len(text)
    for sequence, idx in markup.items():
        value = fastwer.score([sequence[:len_text]], [text], char_level=True)
        if value < THRESHOLD:
            recommend_positions.append((idx, value))
    return recommend_positions


def min_ser_position(positions):
    poses = set([i[0] for i in positions])
    top_pos = (1000, 1000)
    for pos in poses:
        values = [value[1] for value in positions if value[0] == pos]
        if min(values) < top_pos[1]:
            top_pos = (pos, min(values))
    return top_pos


def recommend(text: str) -> tuple or list:
    markup = preprocessing()
    recommend_positions = []
    recommend_positions = search_idx(text, markup, recommend_positions)
    recommend_positions = min_ser_position(recommend_positions)

    if recommend_positions[1] != 1000:
        return recommend_positions


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
        if result:
            return {result[0]: result[1]}


if __name__ == '__main__':
    # print(main('огурцы'))  # {52: 0.0}
    # print(main('морковка нет лук репчатый хотя надо сначала взвесить огурцы'))  # {52: 5.0, 61: 10.0, 51: 25.0}
    print(main(' '.join(sys.argv[1:])))  # python3 recommend.py имбирь конфеты