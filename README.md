# Projects Portfolio of Rodrigo Salazar
Link to [Repo](https://github.com/RodSlzr/portfolio)

## Air Pollution Projects

## - [Air Pollution Estimation](https://github.com/RodSlzr/portfolio/tree/main/Air%20pollution%20estimation)

### Description

To address the lack of comprehensive PM 2.5 data and provide an alternative solution. This project aims to explore the use of Machine Learning. By leveraging location, time, and information from existing sensors, and employing a Random Forest Regressor model in this project, we aim to demonstrate the potential of Machine Learning in estimating PM 2.5 levels and contributing to the monitoring and management of air pollution, particularly in regions with limited sensor coverage.

The OpenAQ data from the Registry of Open Data of AWS was utilized. This dataset offers comprehensive and aggregated physical air quality data from various sources, including government, research-grade, and other publicly available data sources. To focus specifically on Mexico and ensure a relevant and recent dataset, the data request was limited to information from March to May 2023. By leveraging Purple Air's extensive network, which includes a large number of air quality sensors, the dataset obtained for this project consisted of nearly 19 million rows of data.

We achieved an accuracy of 48%, which is significantly better than random guessing with a probability of 1/3, indicating that our model has demonstrated some level of predictive power in forecasting climate factors.

You can read the full project [here](https://github.com/RodSlzr/portfolio/tree/main/Air%20pollution%20estimation), and take a look at the code [here](https://github.com/RodSlzr/portfolio/blob/main/Air%20pollution%20estimation/Final_Project_RS.ipynb).

### Technologies Used

AWS EMR Cluster, PySpark, Pandas, NumPy, Seaborn, and Matplotlib

## - [Air Pollution Mortality](https://github.com/RodSlzr/portfolio/tree/main/Air%20pollution%20mortality)

### Description

Using the database "Mortality, morbidity and welfare cost from exposure to environment-related risks" from the Organization for Economic Co-operation and Development (OCDE), I present a few visualizations that show the evolution of air pollution consequences in terms of lives and welfare costs during the past 30 years.
You can see my visualizations in this [page](https://rodslzr.github.io/portfolio/Air%20pollution%20mortality/Data_Viz/).

Additionally, I did a Machine Learning Project to compare the forecast of the premature deaths due to air pollution in one of the most affected regions, the Balkans, using SVD and LSTM. You can read the project [here](https://rodslzr.github.io/portfolio/Air%20pollution%20mortality/Pollution_in_the_Balkans.pdf ), and take a look at the code [here](https://github.com/RodSlzr/portfolio/blob/main/Air%20pollution%20mortality/Final%20Project%20MFML.ipynb).

### Technologies Used

D3, HTML, CSS, Pandas, NumPy, ARIMA, PyTorch, Matplotlib, and Plotly


## - [Crime Perception in Major US Cities](https://github.com/RodSlzr/portfolio/tree/main/Crime%20perception%20in%20major%20US%20Cities)

### Description

This project explores whether violent sentiment in a city, as represented by tweets, has any correlation with actual crimes in that city and whether that relationship changes over time. We combined tweets containing violent language with FBI data on crimes in the largest US cities from 2005-2021. The dashboard aims to visually display (time and cross-sectional) trends of violent sentiment on twitter and actual crimes to help to discover patterns that relate both sources of data.
Data is disaggregated by type of crime, using FBI categories, and twit category, which was constructed using clustering analysis by topic in Twitter. We used both sentiment analysis (VADER) and clustering techniques (jaccard similarity) to categorize tweets by attitude and category under the umbrella of violent language. This analysis could be a helpful indicator in understanding whether violent sentiment is a lagging or leading indicator of actual crimes and whether a city can change challenging problems both culturally in the way people speak to one another and in terms of actual crime rates.

You can read [here](https://github.com/RodSlzr/portfolio/blob/main/Crime%20perception%20in%20major%20US%20Cities/Capptivators%20Paper%20(1).pdf) the report of the project.

### Technologies Used

Pandas, NumPy, NLTK, Scikit-learn, Twint, Dash, and Plotly.

## - [Stakeholders automated reports](https://github.com/RodSlzr/portfolio/tree/main/Stakeholders%20automated%20reports)

### Description

In 2022, while interning at the Embassy of Mexico in the US, two other interns and I designed and developed a Stakeholders App that generated tailored reports for the embassy on key stakeholders such as congress representatives, business organizations, non-profits, and think tanks. The reports consisted of a political profile section, an economic analysis section, and a press section. They include synthesized relevant information and visuals.

### Technologies Used

Python (Pandas, NumPy, BeautifulSoup, Flask, Jinja, Twint, Matplotlib, SQLite3), Multiple APIs, HTML & CSS.
