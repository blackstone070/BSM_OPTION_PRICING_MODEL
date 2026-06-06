This Project is made to show up skills and knowledge in finance scetor
the project moto is as follows:
Live Website is at https://bsmpricingmodel.streamlit.app
web app that:
1. Takes any stock listed on exchnage (here use yahoo finance to get free data)
2. Fetch live option chain from Yahoo Finance
3. Prices option using Black Schole Model also knwon as BSM and compute famous 5 Greeks(Delta, Gamma, Vega, Theta, Ohm)
4. Visualises all data such as P&L payoff, IV surface, volatility skew 


Follwoing techstack we use :
Backend -> Python + FastAPI
Frontend -> Streamlit (easier than react and good visualization)
Data-> yfinance(free and no API required like Zerodha, Grow)
Math -> numpy + Scipy (use scipy.stats.norm for BSM)
Charts -> Plotly
Deploy -> yet not decide

In first day I would like to end this project
and definitly this Readme is interactive I share my journery my problems and al while writing code.

so 1st thing is to set folders in proper way
There are 3 folder and 2 files outside

bsm-options-pricer/
│
├── app.py                  # Main Streamlit app
├── bsm/
│   ├── __init__.py
│   ├── pricer.py           # BSM formula + all 5 Greeks
│   └── iv_solver.py        # Implied volatility solver
├── data/
│   └── fetcher.py          # yfinance options chain fetcher
├── charts/
│   └── visualisations.py   # All Plotly charts
├── requirements.txt
└── README.md   # where one can find my journery 

We start by wring Requirements.txt file : streamlit>=1.32.0
yfinance>=0.2.40
numpy>=1.26.0
scipy>=1.12.0
plotly>=5.20.0
pandas>=2.2.0

needed this things above 

Sucessfully push first git @11.55pm 
now start building the pricer.py
here we calcualte bsm model as for call option it is 
C(s,t)= N(d1)*s - N(d2)*K*(e**-t)
where d1 = (log(s/k)+ (r+0.5*sigma**2)*t)/(sigma*sqrt(t))
and d2 = d1 -(sigma*sqrt(t))

then calcualte all 5 greeks:
1) delta : tell how price is changing: like for 1 point movement how much point does option move
2) Gamma: It is rate of change of delta which tells speed of delta change
3) Vega: is volatility change , take actual volatility of markt is quite difficult so we consider Implied volatility IV
4) Theta : Price change as per time , at near expiry dela ad gmma of out of money option is zeros only have time vaue ie theta 
5) rho : it tells intreset rate change is directly corealted o pice of underline


Finally It takes me 22 mins to complete this file let push on git

Lets move toward next file as iv_solver.py which is quie easy file i wrte it in 10 mins 
it contain IV calcualtion

Lets move forward now we are at stage 2 
now we fetch data in fetcher.py file 
Done the working o fetching datat where we took specific ticker and download its data and finallly give spot price alng withexpiry and ca;;/ put option informations


now main work is to show the give data for which lets build visuliasation.py file 


Finally we deploy this project after clearing so many bugs and error 
You can visit at https://bsmpricingmodel.streamlit.app website and use this model for free

Hope you enjoy the journey!!
