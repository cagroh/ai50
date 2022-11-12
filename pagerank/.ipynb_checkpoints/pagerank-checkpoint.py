import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # CG: get the list of links for page given in 'page':
    set_of_links = corpus.get(page, "")

    # CG: compute damped probability for links to external pages:
    try:
        damped_probability = damping_factor / len(set_of_links)
    except:
        # CG: if a page has no links, we can pretend it has links to all pages in the corpus, including itself:
        damped_probability = 1 / len(set(corpus.keys()))

    # CG: get the list of all pages in corpus:
    set_of_pages = list(corpus.keys())

    # CG: compute probability of clicking in any link, including a link to same page:
    try:
        remain_probability = (1 - damping_factor) / len(set_of_pages)
    except:
        print ("Given corpus has no pages to process!")
        raise ZeroDivisionError

    # CG: prepare to get the resulting dict:
    resulting_dict = dict()

    # CG: iterate thru the list of pages in the corpus:
    for apage in set_of_pages:        
        # CG: if the page is in the list of links:
        if apage in set_of_links:
            # CG: With probability damping_factor, the random surfer should randomly choose one of the links from page with equal probability.
            resulting_dict.update({apage: remain_probability + damped_probability})
        else:
            # CG: With probability 1 - damping_factor, the random surfer should randomly choose one of all pages in the corpus with equal probability.
            resulting_dict.update({apage: remain_probability})

    # CG: return the resulting dictionary:
    return resulting_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # CG: make sure n is valid:
    if n < 1.0:
        print ("Invalid parameter, 'n' = zero!")
        raise ValueError

    # CG: make sure damping_factor is valid:
    if not 0 < damping_factor < 1.0:
        print ("Invalid parameter, 'damping_factor' = zero!")
        raise ValueError

    # CG: initialize dictionaries:
    pages_sampled = dict()
    resulting_dict = dict()

    # CG: initialize dictionary with keys for each pages and an empty set for the turns of times sampled:
    for apage in list(corpus.keys()):
        pages_sampled.update({apage:[]})

    # CG: randomly select first page:
    current_page = random.choices(list(corpus.keys()))[0]

    # CG: keep count number of samples:
    count = n

    # CG: sampling loop:
    while count:
        # CG: call the transition model for a page:
        result_dict = transition_model(corpus, current_page, damping_factor)
        # CG: updates samples ran for page:
        pages_sampled[current_page].append(count)
        # CG: chooses new page based on the results of last page:
        current_page = random.choices(list(result_dict.keys()), weights=list(result_dict.values()))[0]
        # CG: decrement count:
        count -= 1

    # CG: compute resulting dictionary:
    for apage in list(pages_sampled.keys()):
        resulting_dict.update({apage:len(pages_sampled[apage])/n})

    # CG: return the resulting dictionay:
    return resulting_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # CG: make sure damping_factor is valid:
    if not 0 < damping_factor < 1.0:
        raise ValueError

    # CG: initialize variables:
    page_prob = dict()
    PR = dict()
    oPR=dict()
    list_of_pages = list(corpus.keys())
    list_of_pages_done = []

    # CG: compute N:
    N = len(list_of_pages)

    # CG: compute (1-d) / N:
    common_prob = (1 - damping_factor) / N

    # CG: load initial values into dictionaries:
    for apage in list_of_pages:
        page_prob.update({apage:1/N})
        PR.update({apage:common_prob})

    # CG: loops until differences reach 0.001 of less:
    while list_of_pages_done != list_of_pages:
        # CG: iterates thru the pages in the corpus:
        for p in list_of_pages:
            # CG: iterates thru the pages in the corpus:
            for i in list_of_pages:
                # CG: keep old values for future comparison:
                oPR[p] = PR[p]
                # CG: if page(i) links to page(p), compute and accumulate PR(p): 
                if p in list(corpus[i]):
                    PR[p] = PR[p] + damping_factor * (page_prob[i] / len(list(corpus[i])))
                # CG: if a page has no links, assume it has links to all pages:
                if len(list(corpus[i])) == 0:
                    PR[p] = PR[p] + damping_factor * (page_prob[i] / N)
                
                # CG: if difference between new and previous is 0.001 or less:
                if abs(oPR[p] - PR[p]) <= 0.001:
                    # CG: and the page is not in the list:
                    if p not in list_of_pages_done:
                        # CG: add the page to the list:
                        list_of_pages_done.append(p)

    # CG: return the reulting dictionary:
    return PR


if __name__ == "__main__":
    main()
