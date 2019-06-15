"""Russian Central Bank's web-page parsing
Developer: Ermokhin Stanislav Alexandrovich
Version 1.3.1 (cny added)
"""

from datetime import datetime as dt
from tkinter import Tk, Label, Entry, Button, N, S, W, E
import lxml.html as html
import locale

from OOP import *

language = 'rus' if locale.getlocale()[0][:2] == 'ru' else 'eng'

if language == 'rus':
    import local_rus as local

else:
    import local_eng as local

MAIN_PAGE = 'http://cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.'
CURRENCY_INPUT = 'mode=1&UniDbQuery.date_req1=&UniDbQuery\.date_req2=&UniDbQuery.VAL_NM_RQ='
FR_DATE_INPUT = '&UniDbQuery.FromDate='
TO_DATE_INPUT = '&UniDbQuery.ToDate='
DEFAULT_FR_DATE = '31/01/2018'
DEFAULT_TO_DATE = '31/01/2019'
CURRENCIES = {'usd': 'R01235', 'eur': 'R01239',
              'gbp': 'R01035', 'chf': 'R01775',
              'aud': 'R01010', 'cad': 'R01350',
              'cny': 'R01375'}

root = Tk()
root.title('Currency exchange rates')
root.geometry('700x700')
root.resizable(width=True, height=True)

top_frame = Frame(root)
top_frame.pack()
Label(top_frame, text='From date: ').grid(row=0, column=1)
Label(top_frame, text='To date: ').grid(row=0, column=2)

fr_date = Entry(top_frame)
to_date = Entry(top_frame)

fr_date.insert(0, DEFAULT_FR_DATE)
to_date.insert(0, DEFAULT_TO_DATE)
fr_date.grid(row=1, column=1)
to_date.grid(row=1, column=2)


def mutate_func(lst=None):
    """
    Turn list into dict

    :param lst: list
    :return: dict
    """

    pass_lst = list()
    new_dict = dict()

    try:
        for i in range(2, len(lst), 3):
            pass_lst.append((dt.date(dt.strptime(lst[i - 2],
                                                 '%d.%m.%Y')),
                             float(lst[i-1]),
                             float(lst[i])))

        for tup in pass_lst:
            new_dict[tup[0]] = tup[2]/tup[1]

    except ValueError:
        print('ValueError, returning empty dict')

    return new_dict


def dates(fr_date, to_date):
    """
    From fr_date to to_date rates

    :param fr_date: str
    :param to_date: str
    :return: None
    """

    global graph_page

    exchange_rates = {}

    for currency in CURRENCIES:
        html_table = html.parse(MAIN_PAGE +
                                CURRENCY_INPUT + CURRENCIES[currency] +
                                FR_DATE_INPUT + fr_date + TO_DATE_INPUT +
                                to_date).xpath('//table[@class="data"]')
        try:
            new = [td.text_content().replace(',', '.').split() for td in html_table][0]
            new = new[new.index('Курс')+1:]
            new_dict_for_currency = mutate_func(new)

            exchange_rates[currency] = new_dict_for_currency

        except IndexError:
            pass

    graph_page = PlotWindow(top_frame)
    mpl_subplot = MPLPlot()

    for currency in exchange_rates:
        mpl_subplot.build_plot(([key for key in exchange_rates[currency]]),
                               ([exchange_rates[currency][key]
                                 for key in exchange_rates[currency]]),
                               currency.upper())

    mpl_subplot.suptitle(fr_date + '-' + to_date)
    mpl_subplot.nice_plot('Dates', 'Rates')
    graph_page.add_mpl_figure(mpl_subplot)


def load_button_bound(event=None):
    """
    Bound events on Load button

    :param event: Tk event
    :return: None
    """

    try:
        graph_page.destroy()

    except NameError:
        pass

    dates(fr_date.get(), to_date.get())


def exit_button_bound(event=None):
    """
    Bound events on Exit button

    :param event: Tk event
    :return: None
    """

    root.destroy()

    try:
        exit()

    except KeyboardInterrupt:
        pass


Button(top_frame, width=5, text=local.load_button,
       command=load_button_bound).grid(row=0, column=3, sticky=N+S+W, rowspan=3)

Button(top_frame, width=5, text=local.exit_button,
       command=exit_button_bound).grid(row=0, column=0, sticky=N+S+E, rowspan=3)

Label(top_frame,
      text=local.dates_difference_warning).grid(row=2, column=1,
                                                columnspan=2)

root.bind('<Return>', load_button_bound)
root.bind('<Escape>', exit_button_bound)

root.mainloop()
