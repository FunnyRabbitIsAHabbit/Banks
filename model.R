library(readxl)
library(forecast)
library(stats)

name <- '01.01.2017_01.11.2020.xls'

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

for (col in names(dta)[-c(1)]) {
    fit <- stats::arima(dta[[col]][500:NROW(dta)],
                        order = c(10, 1, 10),
                        method = 'ML')
    print(summary(fit))
    print(plot(stats::acf(fit$residuals,
                          lag.max = 100,
                          plot = FALSE),
               type = 'l'))
    print(plot(forecast::forecast(fit, 7)))
}

# USD go up
