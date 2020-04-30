import matplotlib.pyplot as plt
import itertools
from collections import Counter

ips=['80.234.82.76', "80.299.82.76", "80.239.52.76", '80.239.156.76','80.234.52.76', "80.239.82.76", "80.239.82.76", '80.299.156.76','80.234.52.76', "80.239.82.76", "80.239.82.76", '80.239.156.76','1','2','3','4','5']
color = ["#f0a500","#5a3f11","#708160","#bb3b0e","#8566aa","#c70039","#000000","#27496d","#584153","#c3c3c3"]

def sort_val(to_sort):     
    final_dict = dict(itertools.islice(dict(sorted(dict(Counter(ips)).items(), key=lambda x: x[1], reverse=True)).items(), 10))
    sorted_vals = []
    count = []
    for x in final_dict:
        sorted_vals.append(x)
        count.append(final_dict[x])
    return sorted_vals,count

# Donut
def donut(sorted_val,vals_title):
    sorted_vals,val_count = sort_val(sorted_val)
    sor_val,texts = plt.pie(val_count,colors=color, labels=val_count, pctdistance=0.85, wedgeprops={'edgecolor': '#ffffff'})
    plt.legend(sor_val, sorted_vals, title="Legend", bbox_to_anchor=(0.85, .15, 0.5, 1), loc="upper right",prop={'size': 8})
    my_circle=plt.Circle( (0,0), 0.75, color='white')
    p=plt.gcf()
    plt.title(vals_title)
    p.gca().add_artist(my_circle)
    #plt.show()
donut(ips,"Ips")