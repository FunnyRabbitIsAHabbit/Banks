"""
Russian Central Bank's web-page parsing
Developer: Stanislav Alexandrovich Ermokhin
Version 1.3.4 (data export added)

"""

from datetime import datetime as dt
from operator import itemgetter
from tkinter import Tk, Label, Entry, Button, N, S, W, E, SUNKEN, RAISED
from lxml import etree
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

MAIN_PAGE = 'http://www.cbr.ru/scripts/XML_dynamic.asp?'
CURRENCY_INPUT = '&VAL_NM_RQ='
FR_DATE_INPUT = 'date_req1='
TO_DATE_INPUT = '&date_req2='
DEFAULT_FR_DATE = '31.01.2018'
DEFAULT_TO_DATE = '31.01.2019'
CURRENCIES = {'usd': 'R01235', 'eur': 'R01239',
              'gbp': 'R01035', 'chf': 'R01775',
              'aud': 'R01010', 'cad': 'R01350'}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

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


async def mutate_func(xml):
    """
    Turn xml data into dict

    :param xml: xml
    :return: dict
    """

    new_dict = dict()

    xml = bytes(xml, encoding='windows-1251')
    tree = etree.fromstring(xml)
    obj = tree.xpath('//ValCurs')[0]
    lst = [(obj[i].xpath('//Record[@Date]/@Date')[i],
            obj[i].xpath('//Record//Nominal')[i].text,
            obj[i].xpath('//Record//Value')[i].text.replace(',', '.'))
           for i in range(len(obj))]

    try:
        for obj in lst:
            new_dict[dt.date(dt.strptime(obj[0],
                                         '%d.%m.%Y'))] = float(obj[2])/float(obj[1])

    except ValueError:
        print('ValueError, returning empty dict')

    return new_dict


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text(encoding='windows-1251')


async def wow(url):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        html = await fetch(session, url)

        return await mutate_func(html)


async def exchange_func(fr_date_local, to_date_local):
    """
    Update 'exchange_rates'

    :param fr_date_local: str
    :param to_date_local: str
    :return: None
    """

    global exchange_rates

    for currency in CURRENCIES:
        url = MAIN_PAGE + FR_DATE_INPUT + fr_date_local + TO_DATE_INPUT + to_date_local + \
              CURRENCY_INPUT + CURRENCIES[currency]

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
                      key=itemgetter(0))
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
                   '-'.join(to_date.get().split('/')) + '.xlsx'
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
