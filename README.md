# Shape-of-Stories
A movie script visualizer based on Kurt Vonnegut's rejected thesis on the Shape of Stories. This was a personal project coded in Python using BeautifulSoup for webscraping, Python's Natural Language Toolkit (NLTK) for sentiment analysis, and Dash with Plotly for visualization. 

# Inspiration

I came across a [lecture](https://www.youtube.com/watch?v=GOGru_4z1Vc&t=67s) given by Kurt Vonnegut on his rejected thesis for anthropology studies. As someone who  went through the tedious process of writing a UChicago thesis, I can't help but admire the simplicity of his idea and chuckle knowing my university rejected a paper by one of America's literary greats. The lecture is short enough and delivered with his usual satirical wit, but if pressed for time, a nice visual summary is shown here: 

![alt text](https://i2.wp.com/www.aerogrammestudio.com/wp-content/uploads/2013/03/maya_eilam_vonnegut.png?ssl=1)

As a total movie addict looking to practice data viz techniques, I decided to try coding this up to visualize any movie shape on a y-axis of good to ill fortune.

# Approach

1. Data Collection: I needed a database of movie scripts and IMSDb suited the job perfectly. My program takes a title as user input, uses RegEx to reformat the title as a URL, then requests data from the IMSDb page and parses the script into a dataframe using BeautifulSoup.

2. Data Processing: Movie scripts contain a lot of unusual formatting compared to let's say books or articles, so I remove unnecessary indents and newline characters and drop all NaN values.

3. Sentiment Analysis: Vonnegut plots the shape of stories using a graph layout with the x-axis representing time and the y-axis representing good and ill fortune. I imported Python's NLTK library and used its VADER Sentiment Intensity Analyzer to create a column of raw compound scores from -1 to 1 for each line of the script.

4. Visualization: Using Dash with Plotly, I created a graph figure with x-axis data being the line index numbers and y-axis data being the corresponding sentiment scores.

# Challenges

1. Legibility: Upon first plotting the data, I saw the raw compound scores were too scattered to reveal any discernible pattern. Instead I had to use a rolling average to smooth the curve. This was achieved by adding a new column with Pandas .rolling() function. Given that scripts vary significantly in length and changing the window size of our rolling average altered the shapes signficantly, I added a Dash slider that allows users to control the window size themselves. Additionally, Plotly doesn't have any implicit way of color-coding a filled area chart so needed I split the dataframe into positive and negative scores and graph them independently to improve legibility.

2. Interaction: Although seeing the shapes of movies is cool, and if you know a movie well you might be able to infer what's going on where just by the x-axis, I knew for this tool to be at all useful I needed a way of showing excerpts corresponding to the rise and falls of the plot. This involved learning how to use Hover Data in Dash app callbacks and how to store the script data in a hidden JSON file to be shared amongst all html components. 

# How To Use

1. Download the ShapeOfStories.py file to your computer.
2. In Terminal, navigate to the stored directory and run the following command: python3 ShapeOfStories.py 
3. This will return the following. Copy the URL into your web browser to view the dashboard.

    Dash is running on http://127.0.0.1:8050/

 * Serving Flask app "ShapeOfStories" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)

4. When finished, return to Terminal and press CTRL+C to quit
  
