import pandas as pd
import matplotlib.pyplot as plt

K = 12
team_data = {}
matches_df = pd.read_excel('globalMatches.xlsx')

scores = list(matches_df['Red Score']) + list(matches_df['Blue Score'])
mean = sum(scores) / len(scores)
variance = sum([((x - mean) ** 2) for x in scores]) / len(scores)
sd_score = variance ** 0.5


def ensureKeys(alliance):
    for t in alliance:
        if t not in team_data:
            team_data[t] = 1500


def allianceElo(alliance):
    return sum([team_data[t] for t in alliance])


def updateElos(redAlliance, blueAlliance, scores):
    ensureKeys(redAlliance + blueAlliance)
    red_sum = allianceElo(redAlliance)
    blue_sum = allianceElo(blueAlliance)
    red_win_margin = scores[0] - scores[1]

    predicted_red_win_margin = 0.004 * (red_sum - blue_sum)
    normalized_red_win_margin = red_win_margin / sd_score  # standard deviation
    update = K * (normalized_red_win_margin - predicted_red_win_margin)

    for t in redAlliance:
        team_data[t] += update
    for t in blueAlliance:
        team_data[t] -= update


def buildEloChart(elo_df):
    plt.style.use('ggplot')
    plt.hist(elo_df['Elo'])
    plt.title('FGC 2022 Elo Ratings')
    plt.xlabel('Elo Rating')
    plt.ylabel('# of Teams')
    plt.tight_layout()
    plt.savefig('FGC2022 Elos.png', dpi=600)


def predictRedWin(redAlliance, blueAlliance):
    red_sum = sum([team_data[t] for t in redAlliance])
    blue_sum = sum([team_data[t] for t in blueAlliance])

    return 1 / (1 + 10 ** ((blue_sum - red_sum) / 400))


if __name__ == "__main__":
    for i in range(0, len(matches_df)):
        red = list(matches_df.iloc[i, 1:4])
        blue = list(matches_df.iloc[i, 4:7])
        scores = list(matches_df.iloc[i, 7:9])
        updateElos(red, blue, scores)

    elo_df = pd.DataFrame([{'Team': k, 'Elo': team_data[k]}
                          for k in team_data])
    elo_df.sort_values('Elo', ascending=False).to_csv(
        'globalElos.csv', index=False)
    # print(elo_df.sort_values('Elo', ascending=False).head(
    #     10).to_string(index=False))

    futureMatches = pd.read_excel('globalFuture.xlsx')
    matchPredicts = []
    for i in range(0, len(futureMatches)):
        red = list(futureMatches.iloc[i, 1:4])
        blue = list(futureMatches.iloc[i, 4:7])
        redWin = predictRedWin(red, blue)
        matchPredicts.append(
            {'Match': futureMatches.iloc[i, 0], 'Winner': 'Red' if redWin > 0.5 else 'Blue', 'Red Percent': redWin})
    predict_df = pd.DataFrame(matchPredicts)
    predict_df.to_csv('globalPredict.csv', index=False)
