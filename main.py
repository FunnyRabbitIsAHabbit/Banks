"""Russian Central Bank's web-page parsing
Developer: Ermokhin Stanislav Alexandrovich
Version 1.3 (localization added)"""

import lxml.html as html
from datetime import datetime as dt
from tkinter import Tk, Label, Entry, Button, N, S, W, E
import locale

from OOP import *


language = 'rus' if locale.getlocale()[0][:2] == 'ru' else 'eng'

if language == 'rus':
    import local_rus as local

elif language == 'eng':
    import local_eng as local

else:
    import local_eng as local


MAIN_PAGE = 'http://cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.'
CURRENCY_INPUT = 'mode=1&UniDbQuery.date_req1=&UniDbQuery\.date_req2=&UniDbQuery.VAL_NM_RQ='
fr_date_INPUT = '&UniDbQuery.FromDate='
to_date_INPUT = '&UniDbQuery.ToDate='

DEFAULT_fr_date = '31/01/2018'
DEFAULT_to_date = '31/01/2019'

months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']
days_on_month = {'01': 31, '02': 28, '03': 31, '04': 30,
                 '05': 31, '06': 30, '07': 31, '08': 31,
                 '09': 30, '10': 31, '11': 30, '12': 31}

CURRENCIES = {'usd': 'R01235', 'eur': 'R01239',
              'gbp': 'R01035', 'chf': 'R01775',
              'aud': 'R01010', 'cad': 'R01350'}

# CURRENCIES['cny'] = 'R01375'
# 'cny' does not work properly on larger time scales, though

root = Tk()
root.title('Currency exchange rates')
root.geometry('700x700')
root.resizable(width=True, height=True)

top_frame = Frame(root)
top_frame.pack()
Label(top_frame, text='From date: ').grid(row=0, column=1)
Label(top_frame, text='To date: ').grid(row=0, column=2)

to_date = Entry(top_frame)
fr_date = Entry(top_frame)

fr_date.insert(0, DEFAULT_fr_date)
to_date.insert(0, DEFAULT_to_date)
fr_date.grid(row=1, column=1)
to_date.grid(row=1, column=2)


def dates(fr_date, to_date):
    """From fr_date to to_date rates"""

    global graph_page

    exchange_rates = {}

    for currency in CURRENCIES:
        html_table = html.parse(MAIN_PAGE +
                                CURRENCY_INPUT + CURRENCIES[currency] +
                                fr_date_INPUT + fr_date + to_date_INPUT +
                                to_date).xpath('//table[@class="data"]')
        try:
            new = [td.text_content().replace(',', '.').split() for td in html_table][0]
            new = new[new.index('Курс')+1:]

            if currency == 'cny':
                while '10' in new:
                    new.remove('10')

                try:
                    exchange_rates[currency] = {dt.date(
                        dt.strptime(new[i - 1], '%d.%m.%Y')): float(new[i])/10
                                                for i in range(1, len(new), 2)}

                except ValueError:
                    pass

            else:

                while '1' in new:
                    new.remove('1')

                try:
                    exchange_rates[currency] = {dt.date(
                        dt.strptime(new[i - 1], '%d.%m.%Y')): float(new[i])
                                                for i in range(1, len(new), 2)}

                except ValueError:
                    pass

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


def button_bound(event=None):
    """Bound events on Load button"""

    try:
        graph_page.destroy()

    except NameError:
        pass

    dates(fr_date.get(), to_date.get())


def button_bound1(event=None):
    """Bound events on Exit button"""

    root.destroy()

    try:
        exit()

    except KeyboardInterrupt:
        pass


Button(top_frame, width=5, text=local.load_button,
       command=button_bound).grid(row=0, column=3, sticky=N+S+W, rowspan=3)

Button(top_frame, width=5, text=local.exit_button,
       command=button_bound1).grid(row=0, column=0, sticky=N+S+E, rowspan=3)

Label(top_frame,
      text=local.dates_difference_warning).grid(row=2, column=1,
                                                columnspan=2)

root.bind('<Escape>', button_bound1)
root.bind('<Return>', button_bound)

root.mainloop()
