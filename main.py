from pandas import read_csv, to_datetime
import matplotlib.pyplot as plt


# Wizualizacja danych wejściowych - wykres
def plot_input_data(data_frame):
    plt.figure(figsize=(10, 5))
    plt.plot(to_datetime(data_frame['Data']), data_frame['Zamkniecie'])
    plt.title("Wartości 1000 ostatnich kursów zamknięcia dla indeksu giełdowego WIG20", fontweight="bold")
    plt.xlabel("Data")
    plt.ylabel("Kurs zamknięcia")
    plt.grid()
    plt.savefig('kursy_zamkniecia.png', dpi=600, bbox_inches='tight')
    plt.show()


# Obliczanie średniej kroczącej
def EMA(samples, N, actual):
    alpha = 2 / (N + 1)
    numerator = 0
    denominator = 0

    for i in range(0, N + 1):
        if actual - i >= 0:
            numerator += pow(1 - alpha, i) * samples[actual - i]
            denominator += pow(1 - alpha, i)

    return numerator / denominator


# Obliczanie wartości MACD = EMA12 - EMA26
def MACD(samples, actual):
    if actual >= 26:
        return EMA(samples, 12, actual) - EMA(samples, 26, actual)

    return float('NaN')


# Obliczanie wartości SIGNAL - EMA9 z serii MACD
def SIGNAL(MACD_series, actual):
    if actual >= 26 + 9:
        return EMA(MACD_series, 9, actual)

    return float('NaN')


# Obliczanie serii wartości MACD w kolejnych dniach
def compute_MACD_series(samples):
    MACD_series = []
    for i in range(len(samples)):
        MACD_series.append(MACD(samples, i))

    return MACD_series


# Obliczanie serii wartości SIGNAL w kolejnych dniach
def compute_SIGNAL_series(MACD_series):
    SIGNAL_series = []
    for i in range(len(MACD_series)):
        SIGNAL_series.append(SIGNAL(MACD_series, i))

    return SIGNAL_series


# Rysowanie wykresu MACD/SIGNAL
def plot_MACD_and_SIGNAL(data_frame, MACD_series, SIGNAL_series):
    plt.figure(figsize=(10, 5))
    plt.plot(to_datetime(data_frame['Data']), MACD_series, label="MACD")
    plt.plot(to_datetime(data_frame['Data']), SIGNAL_series, label="SIGNAL")
    plt.title("Wskaźnik MACD wraz z linią sygnału (SIGNAL)", fontweight="bold")
    plt.xlabel("Data")
    plt.ylabel("Wartość MACD/SIGNAL")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig('MACD_SIGNAL.png', dpi=600, bbox_inches='tight')
    plt.show()


# Rysowanie zbiorczego wykresu danych wejściowych oraz MACD z zaznaczonymi momentami kupna/sprzedaży
def plot_buy_and_sell_moments(data_frame, MACD_series, SIGNAL_series):
    fig, axis = plt.subplots(2, figsize=(12, 7), sharex="all")

    axis[0].plot(to_datetime(data_frame['Data']), data_frame['Zamkniecie'])
    axis[0].set_title("Wartości 1000 ostatnich kursów zamknięcia dla indeksu giełdowego WIG20", fontweight="bold")
    axis[0].set_xlabel("Data")
    axis[0].set_ylabel("Kurs zamknięcia")
    axis[0].tick_params(labelbottom=True)

    axis[1].plot(to_datetime(data_frame['Data']), MACD_series, label="MACD")
    axis[1].plot(to_datetime(data_frame['Data']), SIGNAL_series, label="SIGNAL")
    axis[1].set_title("Momenty kupna/sprzedaży na podstawie MACD", fontweight="bold")
    axis[1].set_xlabel("Data")
    axis[1].set_ylabel("Wartość MACD/SIGNAL")

    axis1_buy_marker = True
    axis1_sell_marker = True
    axis0_buy_marker = True
    axis0_sell_marker = True
    for i in range(1, len(MACD_series)):
        if MACD_series[i - 1] < SIGNAL_series[i - 1] and MACD_series[i] > SIGNAL_series[i]:
            axis[1].scatter(to_datetime(data_frame.loc[i, 'Data']), MACD_series[i] - 20, marker="^",
                            color='green', zorder=3, label="Zakup" if axis1_buy_marker else "")
            axis[0].scatter(to_datetime(data_frame.loc[i, 'Data']), data_frame.loc[i, 'Zamkniecie'] - 50, marker="^",
                            color='green', zorder=3, label="Zakup" if axis0_buy_marker else "")
            axis1_buy_marker, axis0_buy_marker = False, False
        elif MACD_series[i - 1] > SIGNAL_series[i - 1] and MACD_series[i] < SIGNAL_series[i]:
            axis[1].scatter(to_datetime(data_frame.loc[i, 'Data']), MACD_series[i] + 20, marker="v",
                            color='red', zorder=3, label="Sprzedaż" if axis1_sell_marker else "")
            axis[0].scatter(to_datetime(data_frame.loc[i, 'Data']), data_frame.loc[i, 'Zamkniecie'] + 50, marker="v",
                            color='red', zorder=3, label="Sprzedaż" if axis0_sell_marker else "")
            axis1_sell_marker, axis0_sell_marker = False, False

    axis[1].legend(loc="lower left")
    axis[0].legend(loc="lower left")
    axis[1].grid()
    axis[0].grid()
    fig.tight_layout()

    plt.savefig('zakup-sprzedaz.png', dpi=600, bbox_inches='tight')
    plt.show()


# Symulacja algorytmu podstawowego
def basic_investing_simulation(data_frame, MACD_series, SIGNAL_series):
    money = 0.0
    stocks = 1000
    for i in range(1, len(MACD_series)):
        if MACD_series[i - 1] < SIGNAL_series[i - 1] and MACD_series[i] > SIGNAL_series[i]:
            stocks += money / data_frame.loc[i, 'Zamkniecie']
            money = 0
        elif MACD_series[i - 1] > SIGNAL_series[i - 1] and MACD_series[i] < SIGNAL_series[i]:
            money += stocks * data_frame.loc[i, 'Zamkniecie']
            stocks = 0

    start_money = round(1000 * data_frame.loc[0, 'Zamkniecie'], 2)
    end_money = round(stocks * data_frame.iloc[-1].loc['Zamkniecie'] + money, 2)
    earned = round(end_money - start_money, 2)
    profit = round(end_money / start_money * 100 - 100, 2)

    print("-------Wyniki algorytmu podstawowego-------")
    print("Kapitał początkowy: ", start_money)
    print("Kapitał końcowy: ", end_money)
    print("Zarobiono: ", earned)
    print("Zysk: ", profit, "%")


# Symulacja własnej propozycji algorytmu
def extended_investing_simulation(data_frame, MACD_series, SIGNAL_series):
    money = 0.0
    stocks = 1000
    for i in range(1, len(MACD_series)):
        if MACD_series[i - 1] < SIGNAL_series[i - 1] and MACD_series[i] > SIGNAL_series[i] and \
                data_frame.loc[i, 'Najwyzszy'] > data_frame.loc[i - 1, 'Najwyzszy']:
            stocks += money / data_frame.loc[i, 'Zamkniecie']
            money = 0
        elif MACD_series[i - 1] > SIGNAL_series[i - 1] and MACD_series[i] < SIGNAL_series[i] and \
                data_frame.loc[i, 'Najnizszy'] < data_frame.loc[i - 1, 'Najnizszy']:
            money += stocks * data_frame.loc[i, 'Zamkniecie']
            stocks = 0

    start_money = round(1000 * data_frame.loc[0, 'Zamkniecie'], 2)
    end_money = round(stocks * data_frame.iloc[-1].loc['Zamkniecie'] + money, 2)
    earned = round(end_money - start_money, 2)
    profit = round(end_money / start_money * 100 - 100, 2)

    print("\n-------Wyniki własnego algorytmu-------")
    print("Kapitał początkowy: ", start_money)
    print("Kapitał końcowy: ", end_money)
    print("Zarobiono: ", earned)
    print("Zysk: ", profit, "%")


# Punkt startowy programu - wywołanie poszczególnych funkcji
def main():
    data_frame = read_csv("wig20_d.csv")
    plot_input_data(data_frame)
    MACD_series = compute_MACD_series(data_frame['Zamkniecie'].tolist())
    SIGNAL_series = compute_SIGNAL_series(MACD_series)
    plot_MACD_and_SIGNAL(data_frame, MACD_series, SIGNAL_series)
    plot_buy_and_sell_moments(data_frame, MACD_series, SIGNAL_series)

    basic_investing_simulation(data_frame, MACD_series, SIGNAL_series)
    extended_investing_simulation(data_frame, MACD_series, SIGNAL_series)


if __name__ == "__main__":
    main()
