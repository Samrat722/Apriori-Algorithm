import csv
import sys
import argparse
import time
import io
from flask import Flask, request, render_template
from collections import defaultdict, Counter
from itertools import combinations

app = Flask(__name__)

# def load_transactions(file_name):
#     transactions = []
#     with open(file_name, 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             transactions.append(set(row))
#     return transactions

def get_frequent_1_itemsets(transactions, min_support):
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

def apriori_gen(itemsets, k):
    candidates = set()
    itemsets = list(itemsets)
    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            union_set = itemsets[i] | itemsets[j]
            if len(union_set) == k and not has_infrequent_subset(union_set, itemsets):
                candidates.add(union_set)
    return candidates

def has_infrequent_subset(candidate, frequent_itemsets):
    for subset in combinations(candidate, len(candidate) - 1):
        if frozenset(subset) not in frequent_itemsets:
            return True
    return False

def filter_candidates(transactions, candidates, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                item_counts[candidate] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

def apriori(transactions, min_support):
    frequent_itemsets = []
    current_itemsets = get_frequent_1_itemsets(transactions, min_support)
    k = 2
    while current_itemsets:
        frequent_itemsets.extend(current_itemsets.keys())
        candidates = apriori_gen(current_itemsets.keys(), k)
        current_itemsets = filter_candidates(transactions, candidates, min_support)
        k += 1
    return [set(itemset) for itemset in frequent_itemsets] 
    
def get_maximal_frequent_itemsets(frequent_itemsets):
    maximal = []
    for itemset in sorted(frequent_itemsets, key=len, reverse=True):
        if not any(set(itemset).issubset(set(max_itemset)) for max_itemset in maximal):
            maximal.append(itemset)
    return maximal

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/main.csv', methods=['POST'])
def main():
    # parser = argparse.ArgumentParser(description='Apriori Algorithm Implementation')
    # parser.add_argument('-i', '--input', required=True, help='Input CSV file')
    # parser.add_argument('-m', '--min_support', type=int, required=True, help='Minimum support value')
    # args = parser.parse_args()
    file = request.files['file']
    # transactions = load_transactions(args.input)
    min_support = int(request.form['min_support'])
    stream = io.StringIO(file.tream.read().decode("UTF8"), newline=None)
    transactions =[set(row) for row in csv.reader(stream)]
    start_time = time.time() 
    frequent_itemsets = apriori(transactions, min_support)
    end_time = time.time()
    execution_time = end_time - start_time
    maximal_frequent_itemsets = get_maximal_frequent_itemsets(frequent_itemsets)
    maximal_frequent_itemsets.sort(key=lambda x: (len(x), x))
    total_count = len(maximal_frequent_itemsets)
    # print(f"Input file: {args.input}")
    # print(f"Minimal support: {min_support}")
    # print("{", end="")
    formatted_itemsets = [f"{{{','.join(map(str, itemset))}}}" for itemset in maximal_frequent_itemsets]

    result_format = "("+"".join(formatted_itemsets) +")"
    return render_template(
    'result.html',
    minimal_support = min_support,
    execution_time=f"{execution_time:.2f} seconds",
    total_count= total_count,
    result=result_string
    )  

if __name__ == '__main__':
    main()
app.run(host="0.0.0.0", port=5000)
