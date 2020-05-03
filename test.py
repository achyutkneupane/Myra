import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
import whois
my_list = ['mtalk.google.com', '43.courier-push-apple.com.akadns.net', 'asimov.vortex.data.microsoft.com.akadns.net', 'gs-loc-new.ls-apple.com.akadns.net', '50-courier.push.apple.com', '41-courier.push.apple.com', 'mtalk.google.com', 'update.code.visualstudio.com', 'asimov.vortex.data.microsoft.com.akadns.net']
stop_words = ["net"] + list(STOPWORDS)
whois_data = []

wordcloud = WordCloud(width = 1000, height = 500, stopwords=stop_words, margin=20, include_numbers=False,repeat=False,contour_color="pink").generate(unique_string)
plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
#plt.savefig("your_file_name"+".png", bbox_inches='tight')
plt.show()
plt.close()