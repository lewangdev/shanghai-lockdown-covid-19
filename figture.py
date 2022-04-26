import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from util import get_data


def generate_figtures():
    new_cases = get_data()
    x = [new_case["date"].replace("2022-", "") for new_case in new_cases]
    y = [new_case["total"] for new_case in new_cases]
    plt.figure(figsize=(12, 5))
    plt.xlabel("Date")
    plt.ylabel("Cases")
    plt.grid(True, axis="y")
    plt.plot(x, y, color="red")
    plt.xticks(rotation=45)
    plt.savefig('figture/new-cases.png', format='png', dpi=300)

    total = 0
    cases = []
    for new_case in new_cases:
        total = new_case["total"] + total
        cases.append(dict(date=new_case["date"], total=total))
    x = [case["date"].replace("2022-", "") for case in cases]
    y = [case["total"] for case in cases]
    plt.figure(figsize=(12, 5))
    plt.xlabel("Date")
    plt.ylabel("Cases")
    plt.grid(True, axis="y")
    plt.plot(x, y, color="red")
    plt.xticks(rotation=45)
    plt.savefig('figture/cases.png', format='png', dpi=300)


if __name__ == "__main__":
    generate_figtures()
