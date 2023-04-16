from flask import *
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import string


import nltk
import re


app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def enter():
    print(request.method)
    if request.method == "GET":
        return render_template("second.html")
    return redirect(url_for("home"))

@app.route('/res',methods=['GET','POST'])
def home():
    if request.method == "POST":
        f = request.files['attachment']
        f.save("static/sample.csv")
        from nltk.corpus import stopwords
        data = pd.read_csv(r"static/sample.csv",encoding = 'latin1')
        #nltk.download('stopwords')
        stemmer = nltk.SnowballStemmer("english")
        stopword=set(stopwords.words('english'))

        def clean(text):
            text = str(text).lower()
            text = re.sub('\[.*?\]', '', text)
            text = re.sub('https?://\S+|www\.\S+', '', text)
            text = re.sub('<.*?>+', '', text)
            text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
            text = re.sub('\n', '', text)
            text = re.sub('\w*\d\w*', '', text)
            text = [word for word in text.split(' ') if word not in stopword]
            text=" ".join(text)
            text = [stemmer.stem(word) for word in text.split(' ')]
            text=" ".join(text)
            return text
        data["Review"] = data["Review"].apply(clean)

        text = " ".join(i for i in data['Review'])
        stopwords = set(STOPWORDS)
        wordcloud = WordCloud(stopwords=stopwords,background_color="white").generate(text)
        sentiments = SentimentIntensityAnalyzer()
        data["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in data["Review"]]
        data["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in data["Review"]]
        data["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in data["Review"]]
        data = data[["Review", "Positive", "Negative", "Neutral"]]
        print(data.head())


        x = sum(data["Positive"])
        y = sum(data["Negative"])
        z = sum(data["Neutral"])
        print("Positive: ", x)
        print("Negative: ", y)
        print("Neutral:",z)
        data.to_csv('final.csv')
        return render_template("index.html",res=1,data=[x,y,z])
    else:
        return render_template("index.html")

@app.route('/download')
def download():
    
    fe='final.csv'
    return send_file(fe,as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
