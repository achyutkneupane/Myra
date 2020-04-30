
import matplotlib.pyplot as plt
import itertools
from collections import Counter
import squarify

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
def donut(to_sort_val,vals_title):
    sorted_vals,val_count = sort_val(to_sort_val)
    sor_val,texts = plt.pie(val_count,colors=color, labels=val_count, pctdistance=0.85, wedgeprops={'edgecolor': '#ffffff'})
    plt.legend(sor_val, sorted_vals, title="Legend", bbox_to_anchor=(0.85, .15, 0.5, 1), loc="upper right",prop={'size': 8})
    my_circle=plt.Circle( (0,0), 0.75, color='white')
    p=plt.gcf()
    plt.title(vals_title)
    p.gca().add_artist(my_circle)
    plt.show()
#donut(ips,"Ips")


import squarify
def tree(to_sort_val):
    label_data = []
    plt.figure(figsize=(6,3))
    sorted_vals,val_count = sort_val(to_sort_val)
    for x in range(10):
        label_data.append("%s\nCount : %s" %(sorted_vals[x],val_count[x]))
    print(label_data)
    squarify.plot(sizes=val_count, label=label_data, color=color, alpha=.6, edgecolor="white", linewidth=2, pad=True, text_kwargs={'fontsize':7.3})
    plt.axis('off')
    plt.show()

tree(ips)