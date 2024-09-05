from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

# don't change this
matplotlib.use('Agg')
app = Flask(__name__) # do not change this

# Insert the web scraping process here
url = 'https://www.boxofficemojo.com/year/world/'
url_get = requests.get(url)
soup = BeautifulSoup(url_get.content, "html.parser")

# Find the table
table = soup.find('table')
rows = table.find_all('tr')[1:]  # Skip the header row

# Extract data
data = []
for row in rows:
    columns = row.find_all('td')
    data.append([column.text.strip() for column in columns])

# Extract headers
headers = [header.text.strip() for header in table.find_all('th')]

# Change into DataFrame
df = pd.DataFrame(data, columns=headers)

df.columns=["Rank", "Movie Title", "Worldwide", "Domestic", "Percent Domestic", "Foreign", "Percent Foreign"]

# Insert data wrangling here
df['Worldwide'] = df['Worldwide'].replace({'\$': '', ',': ''}, regex=True)
df['Domestic'] = df['Domestic'].replace({'\$': '', ',': ''}, regex=True)
df['Foreign'] = df['Foreign'].replace({'\$': '', ',': ''}, regex=True)
df['Percent Foreign'] = df['Percent Foreign'].replace({'%': '', ',': ''}, regex=True)
df['Percent Domestic'] = df['Percent Domestic'].replace({'%': '', ',': ''}, regex=True)

df['Worldwide'] = pd.to_numeric(df['Worldwide'], errors='coerce', )
df['Domestic'] = pd.to_numeric(df['Domestic'], errors='coerce')
df['Foreign'] = pd.to_numeric(df['Foreign'], errors='coerce')
df['Percent Foreign'] = pd.to_numeric(df['Percent Foreign'], errors='coerce')
df['Percent Domestic'] = pd.to_numeric(df['Percent Domestic'], errors='coerce')

df.dropna(inplace=True)
# End of data wrangling

@app.route("/")
def index():
    # Prepare card data (average worldwide revenue, for example)
    card_data = f'{df["Worldwide"].mean().round(2)}'  # Calculate the mean worldwide revenue and round it

    # Generate plot (for example, a bar plot of top 10 movies by worldwide revenue)
    top_10_movies = df.sort_values('Worldwide', ascending=False).head(10)
    plt.figure(figsize=(20, 9))
    ax = top_10_movies.plot(kind='barh', x='Title', y='Worldwide', color='blue', legend=False)
    plt.title('Top 10 Movies by Worldwide Revenue')
    plt.xlabel('Revenue (in USD)')
    plt.ylabel('Movie Title')
    plt.tight_layout()

    # Rendering plot
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]

    # Render to HTML template
    return render_template('index.html',
                           card_data=card_data, 
                           plot_result=plot_result)

if __name__ == "__main__":
    app.run(debug=True)
