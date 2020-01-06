"""
Russian Central Bank's web-page parsing
Developer: Stanislav Alexandrovich Ermokhin
Version 1.3.3 (data export added)

"""

from datetime import datetime as dt
from tkinter import Tk, Label, Entry, Button, N, S, W, E, SUNKEN, RAISED
import lxml.html as h
import locale
import aiohttp
import asyncio
import pandas as pd

from OOP import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

try:
    language = 'rus' if locale.getlocale()[0][:2] == 'ru' else 'eng'

    if language == 'rus':
        import local_rus as local

    else:
        import local_eng as local

except ValueError:
    import local_eng as local

MAIN_PAGE = 'http://cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.'
CURRENCY_INPUT = 'mode=1&UniDbQuery.date_req1=&UniDbQuery\.date_req2=&UniDbQuery.VAL_NM_RQ='
FR_DATE_INPUT = '&UniDbQuery.FromDate='
TO_DATE_INPUT = '&UniDbQuery.ToDate='
DEFAULT_FR_DATE = '31/01/2018'
DEFAULT_TO_DATE = '31/01/2019'
CURRENCIES = {'usd': 'R01235', 'eur': 'R01239',
              'gbp': 'R01035', 'chf': 'R01775',
              'aud': 'R01010', 'cad': 'R01350'}

exchange_rates = dict()

root = Tk()
root.title('Currency exchange rates')
root.geometry('700x700')
root.resizable(width=True,
               height=True)

top_frame = Frame(root)
top_frame.pack()
Label(top_frame,
      text='From date: ').grid(row=0, column=1)
Label(top_frame,
      text='To date: ').grid(row=0, column=2)

fr_date = Entry(top_frame)
to_date = Entry(top_frame)

fr_date.insert(0, DEFAULT_FR_DATE)
to_date.insert(0, DEFAULT_TO_DATE)
fr_date.grid(row=1, column=1)
to_date.grid(row=1, column=2)


def mutate_func(html=None):
    """
    Turn html data into dict

    :param html: html
    :return: dict
    """

    pass_lst = list()
    new_dict = dict()

    html_table = h.document_fromstring(html).xpath('//table[@class="data"]')
    new = [td.text_content().replace(',', '.').split() for td in html_table][0]
    lst = new[new.index('Курс') + 1:]

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


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def wow(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)

        return mutate_func(html)


async def exchange_func(fr_date_local, to_date_local):
    """
    Update 'exchange_rates'

    :param fr_date_local: str
    :param to_date_local: str
    :return: None
    """

    global exchange_rates

    for currency in CURRENCIES:
        url = MAIN_PAGE + CURRENCY_INPUT + CURRENCIES[currency] + \
              FR_DATE_INPUT + fr_date_local + TO_DATE_INPUT + to_date_local

        exchange_rates[currency] = await wow(url)


def dates():
    """
    From fr_date to to_date rates

    :return: None
    """

    global graph_page

    asyncio.run(exchange_func(fr_date.get(), to_date.get()))

    graph_page = PlotWindow(top_frame)
    mpl_subplot = MPLPlot()

    for currency in exchange_rates:
        data = sorted([(key, exchange_rates[currency][key])
                       for key in exchange_rates[currency]],
                      key=lambda x: x[0])
        mpl_subplot.build_plot(([item[0] for item in data]),
                               ([item[1] for item in data]),
                               currency.upper())

    mpl_subplot.suptitle(fr_date.get() + '-' + to_date.get())
    mpl_subplot.nice_plot('Dates', 'Rates')
    graph_page.add_mpl_figure(mpl_subplot)


def load_button_bound(event=None):
    """
    Bound events on Load button

    :param event: Tk event
    :return: None
    """

    global graph_page
    load_button.config(relief=SUNKEN)

    try:
        graph_page.destroy()

    except NameError:
        pass

    dates()
    load_button.config(relief=RAISED)


def data_load_button_bound(event=None):
    """
    Bound events on Load Data button

    :param event: Tk event
    :return: None
    """

    data_load_button.config(relief=SUNKEN)
    new_filename = '-'.join(fr_date.get().split('/')) + '_' + \
                   '-'.join(to_date.get().split('/')) + '.xls'
    asyncio.run(exchange_func(fr_date.get(), to_date.get()))

    with pd.ExcelWriter(path=new_filename) as excel_writer:
        for currency in exchange_rates:
            currency_data = [(key, exchange_rates[currency][key])
                             for key in exchange_rates[currency]]
            df = pd.DataFrame(data=currency_data,
                              columns=['Date', 'Rate'])
            df.sort_values(by=['Date'])
            df.to_excel(excel_writer=excel_writer,
                        sheet_name=currency,
                        index=False)

    data_load_button.config(relief=RAISED)


def exit_button_bound(event=None):
    """
    Bound events on Exit button

    :param event: Tk event
    :return: None
    """

    exit_button.config(relief=SUNKEN)
    root.destroy()

    try:
        exit()

    except KeyboardInterrupt:
        pass


data_load_button = Button(top_frame,
                          width=10, text=local.data_load_button,
                          command=data_load_button_bound)
data_load_button.grid(row=0, column=4, sticky=N+S+W, rowspan=3)

load_button = Button(top_frame,
                     width=10, text=local.load_button,
                     command=load_button_bound)
load_button.grid(row=0, column=3, sticky=N+S+W, rowspan=3)

exit_button = Button(top_frame,
                     width=10, text=local.exit_button,
                     command=exit_button_bound)
exit_button.grid(row=0, column=0, sticky=N+S+E, rowspan=3)

Label(top_frame,
      text=local.dates_difference_warning).grid(row=2, column=1,
                                                columnspan=2)

root.bind('<Return>', load_button_bound)
root.bind('<Escape>', exit_button_bound)

root.mainloop()
