import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
from whois import whois,parser
from socket import gaierror,socket,timeout
stop_words = ["net","io","co"] + list(STOPWORDS)
whois_data = []
name = []
textt = ['gitlab.com', 'github.com', 'mnsvmag.com', 'logpoint.com']
def whois_dns(domain_list):
    for dns_str in domain_list:
        try:
            name = whois(dns_str)
        except parser.PywhoisError: pass
        except AttributeError: pass
        except gaierror: pass
        except timeout: pass
        try:
            if len(name.domain_name) == 2:
                whois_data.append(name.domain_name[0])
            elif len(name.domain_name) > 1:
                whois_data.append(name.domain_name)
        except AttributeError: pass
        except TypeError: pass
    whois_str = (" ").join(whois_data)
    return whois_str

def word_cloud(dns_list):
    text_str = whois_dns(dns_list)
    dns_wc = WordCloud(
        width = 1000,
        height = 500,
        stopwords=stop_words,
        margin=20,
        include_numbers=False,
        repeat=False).generate(text_str)
    plt.figure(figsize=(15,8))
    plt.imshow(dns_wc)
    plt.axis("off")
    plt.title("DNS Word Cloud")
    plt.show()
    plt.close()

word_cloud(textt)