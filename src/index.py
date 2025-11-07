from varasto import Varasto


def main():
    mehua = Varasto(100.0)
    olutta = Varasto(100.0, 20.2)

    print("Luonnin jälkeen:")
    print(f"Mehuvarasto: {mehua}")
    print(f"Olutvarasto: {olutta}")

    print("Olut getterit:")
    print(f"saldo = {olutta.saldo}")
    print(f"tilavuus = {olutta.tilavuus}")
    print(f"paljonko_mahtuu = {olutta.paljonko_mahtuu()}")
    # ohtuvarasto
# ohtuvarasto

![GHA workflow badge](https://github.com/serze10/ohtuvarasto/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/github/serze10/ohtuvarasto/graph/badge.svg?token=LY1T5DMW2Z)](https://codecov.io/github/serze10/ohtuvarasto)
[![Pylint](https://github.com/santersi/ohtuvarasto/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/santersi/ohtuvarasto/actions/workflows/pylint.yml)



![GHA workflow badge](https://github.com/serze10/ohtuvarasto/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/github/serze10/ohtuvarasto/graph/badge.svg?token=LY1T5DMW2Z)](https://codecov.io/github/serze10/ohtuvarasto)
[![Pylint](https://github.com/santersi/ohtuvarasto/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/santersi/ohtuvarasto/actions/workflows/pylint.yml)

 

if __name__ == "__main__":
    main()
