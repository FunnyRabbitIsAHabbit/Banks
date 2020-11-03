library(readxl)
library(forecast)
library(stats)

name <- '31.01.2000_03.11.2020.xlsx'

usd_data <- readxl::read_excel(name,
                               sheet = 'usd')
eur_data <- readxl::read_excel(name,
                               sheet = 'eur')
chf_data <- readxl::read_excel(name,
                               sheet = 'chf')
dta <- data.frame(date = usd_data$Date,
                  usd = usd_data$Rate,
                  eur = eur_data$Rate,
                  chf = chf_data$Rate)
print(dta)

for (col in names(dta)[-1]) {
    print(col)
    print(forecast::ndiffs(dta[[col]], test = 'pp'))
    fit <- stats::arima(dta[[col]],
                        order = c(10, 1, 10),
                        method = 'ML')
    print(summary(fit))
    print(plot(stats::acf(fit$residuals,
                          lag.max = 100,
                          plot = FALSE),
               type = 'l'))
    fcst_dta <- forecast::forecast(fit, 100)
    print(plot(fcst_dta))
}

# USD go up
