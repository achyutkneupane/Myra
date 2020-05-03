
import matplotlib.pyplot as plt
import itertools
from collections import Counter
import matplotlib
import squarify

ips=['80.234.82.76', "80.299.82.76", "80.239.52.76", '80.239.156.76','80.234.52.76', "80.239.82.76", "80.239.82.76", '80.299.156.76','80.234.52.76', "80.239.82.76", "80.239.82.76", '80.239.156.76','1','2','3','4','5']
color = ["#1d0027","#23042b","#2d0e37","#3b2141","#49354e","#5b4a5f","#69586e","#7f7383","#98949a","#e3e3e3"]

plt.style.use('dark_background')
def sort_val(to_sort):     
    final_dict = dict(itertools.islice(dict(sorted(dict(Counter(ips)).items(), key=lambda x: x[1], reverse=True)).items(), 10))
    sorted_vals = []
    count = []
    for x in final_dict:
        sorted_vals.append(x)
        count.append(final_dict[x])
    return sorted_vals,count

# Donut
def donut(to_sort_val,vals_title):
    sorted_vals,val_count = sort_val(to_sort_val)
    sor_val,texts = plt.pie(val_count,colors=color, labels=val_count, pctdistance=0.85, wedgeprops={'edgecolor': 'black'})
    plt.legend(sor_val, sorted_vals, title="Legend", bbox_to_anchor=(0.85, .15, 0.5, 1), edgecolor="black", loc="upper right", prop={'size': 8})
    my_circle=plt.Circle( (0,0), 0.75, color='black')
    p=plt.gcf()
    plt.title(vals_title)
    p.gca().add_artist(my_circle)
    plt.show()
donut(ips,"Ips")


import squarify
def tree(to_sort_val):
    label_data = []
    plt.figure(figsize=(12,6))
    sorted_vals,val_count = sort_val(to_sort_val)
    for x in range(len(sorted_vals)):
        label_data.append("%s\nCount : %s" %(sorted_vals[x],val_count[x]))
    cmap = matplotlib.cm.Purples
    mini=min(val_count)
    maxi=max(val_count)
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in val_count]
    squarify.plot(sizes=val_count, label=sorted_vals, alpha=.8, color=colors )
    plt.axis('off')
    plt.title("Kando")
    plt.show()

tree(ips)


from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

text=("The beginning and ending colors are captured from the GET request to the server. After range checking of the colors and the number of steps requested, a loop is run and the RGB components are linearly interpolated according to the current step of the loop. The color generated is used as the background of the table row. The color values are provided on each row in both decimal and hexadecimal. The ordering for the values in black text are: index number, percentage of interpolation, decimal value of the background color, hexadecimal value of the background color. The ordering of the white text is a mirror of the ordering of the black text. Obviously, the black and white provide enough redundancy so that at least one set of values is readable (having high enough contrast with the background to be read) no matter what begin and end colors are chosen. Source code for the color gradient generator may be found here. It's a PHP file, but it has a .txt final extension to make it easier to download from the web server. A final caveat: the html, head, and body tags are not included in this file. The file was meant to be included into a host document. In fact, this document hosts the source file directly with a PHP include.")

wordcloud = WordCloud(width=480, height=480, margin=0).generate(text)
 
# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()
